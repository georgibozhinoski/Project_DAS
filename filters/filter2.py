import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")


def fetch_issuers_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM issuers")
    issuers = cursor.fetchall()
    conn.close()
    return issuers


def scrape_data(issuer_code, from_date, to_date, session):
    print(f"Fetching data from {from_date.strftime('%d.%m.%Y')} to {to_date.strftime('%d.%m.%Y')} for issuer {issuer_code}")
    url = 'https://www.mse.mk/mk/stats/symbolhistory/kmb'
    params = {
        'Code': issuer_code,
        'FromDate': from_date.strftime("%d.%m.%Y"),
        'ToDate': to_date.strftime("%d.%m.%Y")
    }
    response = session.get(url, params=params)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    data = []

    # Table Selector for data
    table = soup.find('table', {'id': 'resultsTable'})
    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if cols:
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
        print(f"Retrieved {len(data)} rows for {issuer_code} from {from_date.strftime('%d.%m.%Y')} to {to_date.strftime('%d.%m.%Y')}")
    else:
        print(f"No data found for {issuer_code} from {from_date.strftime('%d.%m.%Y')} to {to_date.strftime('%d.%m.%Y')}")
    return data


def fetch_data_for_issuer(issuer, session):
    issuer_code, issuer_name = issuer
    today = datetime.now()
    start_date = datetime(2014, 1, 1)
    all_data = []

    print(f"\nStarting data fetch for issuer: {issuer_name} ({issuer_code})")

    while start_date < today:
        to_date = min(start_date + timedelta(days=364), today)  # Using 1-year intervals
        data_chunk = scrape_data(issuer_code, start_date, to_date, session)

        if data_chunk:
            all_data.extend([(issuer_code, *row) for row in data_chunk])

        start_date = to_date + timedelta(days=1)
        print(f"Completed fetching data up to {to_date.strftime('%Y-%m-%d')} for {issuer_name}.")

    return all_data


def main():
    start_time = time.time()  # Start the timer
    issuers = fetch_issuers_from_db()
    all_data = []

    with requests.Session() as session:
        with ThreadPoolExecutor(max_workers=21) as executor:  # Increased max_workers
            futures = {executor.submit(fetch_data_for_issuer, issuer, session): issuer for issuer in issuers}
            for future in as_completed(futures):
                issuer = futures[future]
                try:
                    issuer_data = future.result()
                    all_data.extend(issuer_data)
                    print(f"Completed data collection for issuer: {issuer[1]} ({issuer[0]}).")
                except Exception as e:
                    print(f"Error fetching data for issuer {issuer[1]} ({issuer[0]}): {e}")

    print(f"\nData fetching complete. Total records collected: {len(all_data)}")

    end_time = time.time()  # End the timer
    print(f"Total time taken: {end_time - start_time:.2f} seconds")


if __name__ == "__main__":
    main()
