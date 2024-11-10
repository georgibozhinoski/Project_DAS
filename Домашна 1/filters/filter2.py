import os
import sqlite3
import time
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")

def fetch_issuer_codes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM issuers ORDER BY code ASC")
    issuers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return issuers

def fetch_last_available_date(issuer_code):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT date FROM historical_data 
            WHERE issuer_code = ? 
            ORDER BY date DESC 
            LIMIT 1
        """, (issuer_code,))
        row = cursor.fetchone()
        if row:
            newest_date_str = row[0]
            newest_date = datetime.strptime(newest_date_str, "%Y-%m-%d")
            return newest_date
        else:
            return None
    except sqlite3.Error:
        return None
    finally:
        conn.close()

def get_date_ranges(start_date, end_date, days_per_chunk=340):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%m-%d-%Y")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%m-%d-%Y")
    date_ranges = []
    current_start = start_date
    while current_start <= end_date:
        current_end = min(current_start + timedelta(days=days_per_chunk - 1), end_date)
        date_ranges.append((current_start.strftime("%m-%d-%Y"), current_end.strftime("%m-%d-%Y")))
        current_start = current_end + timedelta(days=1)
    return date_ranges

def fetch_and_parse_issuer_data(issuer_code, start_date, end_date):
    base_url = f"https://www.mse.mk/en/stats/symbolhistory/{issuer_code}"
    date_ranges = get_date_ranges(start_date, end_date)
    issuer_data = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for start_date_range, end_date_range in date_ranges:
        response = requests.get(base_url,
                                params={"FromDate": start_date_range.replace("-", "/"),
                                        "ToDate": end_date_range.replace("-", "/")},
                                headers=headers)
        if response.status_code == 200:
            parsed_data = parse_data_from_html(response.text, issuer_code)
            issuer_data.extend(parsed_data)
    return issuer_data

def parse_data_from_html(html_content, issuer_code):
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", id="resultsTable")
    data = []
    if table:
        rows = table.find_all("tr")
        for row in rows[1:]:
            columns = row.find_all("td")
            if len(columns) == 9:
                data.append((issuer_code,
                             columns[0].text.strip(),
                             columns[1].text.strip().replace(",", ""),
                             columns[2].text.strip().replace(",", ""),
                             columns[3].text.strip().replace(",", ""),
                             columns[4].text.strip().replace(",", ""),
                             columns[5].text.strip(),
                             columns[6].text.strip().replace(",", ""),
                             columns[7].text.strip().replace(",", ""),
                             columns[8].text.strip().replace(",", "")))
    return data

def insert_data_into_db_bulk(data):
    if not data:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL;')
    cursor = conn.cursor()
    try:
        cursor.executemany('''INSERT OR IGNORE INTO historical_data (
                issuer_code, date, last_price, max_price, min_price, avg_price, percent_change, quantity, turnover_best, total_turnover
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    finally:
        conn.close()

def sort_and_format_data(issuer_data):
    formatted_data = []
    for record in issuer_data:
        issuer_code, date_str, *other_data = record
        date_obj = datetime.strptime(date_str, "%m/%d/%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        formatted_data.append((issuer_code, formatted_date, *other_data))
    formatted_data.sort(key=lambda x: (x[0], x[1]))
    sorted_data = []
    current_issuer = None
    issuer_group = []
    for record in formatted_data:
        issuer_code, date_str, *other_data = record
        if issuer_code != current_issuer:
            if issuer_group:
                is_sorted = all(
                    issuer_group[i][1] >= issuer_group[i + 1][1]
                    for i in range(len(issuer_group) - 1)
                )
                if not is_sorted:
                    issuer_group.sort(key=lambda x: x[1], reverse=True)
                sorted_data.extend(issuer_group)
            issuer_group = [(issuer_code, date_str, *other_data)]
            current_issuer = issuer_code
        else:
            issuer_group.append((issuer_code, date_str, *other_data))
    if issuer_group:
        is_sorted = all(
            issuer_group[i][1] >= issuer_group[i + 1][1]
            for i in range(len(issuer_group) - 1)
        )
        if not is_sorted:
            issuer_group.sort(key=lambda x: x[1], reverse=True)
        sorted_data.extend(issuer_group)
    return sorted_data

def main():
    start_time = time.time()
    issuer_codes = fetch_issuer_codes()
    end_date = datetime.today()
    start_date_no_data = datetime(end_date.year - 10, 1, 1)
    all_issuer_data = []
    issuers_inserted = 0
    chunk_size = 100
    total_issuers = len(issuer_codes)
    for i in range(0, total_issuers, chunk_size):
        chunk = issuer_codes[i:i + chunk_size]
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = []
            for issuer_code in chunk:
                last_available_date = fetch_last_available_date(issuer_code)
                if last_available_date:
                    continue
                start_date = start_date_no_data
                futures.append(executor.submit(fetch_and_parse_issuer_data, issuer_code, start_date, end_date))
            for future in as_completed(futures):
                issuer_data = future.result()
                if issuer_data:
                    all_issuer_data.extend(issuer_data)
    all_issuer_data = sort_and_format_data(all_issuer_data)
    insert_data_into_db_bulk(all_issuer_data)
    issuers_inserted = len(issuer_codes)
    print(f"Data collection completed in {time.time() - start_time:.2f} seconds.")
    print(f"Data was inserted for {issuers_inserted} issuers.")

if __name__ == "__main__":
    main()
