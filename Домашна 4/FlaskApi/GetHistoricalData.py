from flask import Flask, jsonify, request
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)

SPRING_API_URL_ISSUERS = "http://localhost:8080/api/issuers"
SPRING_API_URL_HISTORICAL = "http://localhost:8080/api/historicaldata"
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")


def fetch_issuer_codes():
    try:
        response = requests.get(SPRING_API_URL_ISSUERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching issuers: {e}")
        return []


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


def send_data_to_spring_api(data):
    try:
        formatted_data = [
            {
                "issuerCode": record[0],
                "date": record[1],
                "lastPrice": format_price(record[2]),
                "maxPrice": format_price(record[3]),
                "minPrice": format_price(record[4]),
                "avgPrice": format_price(record[5]),
                "percentChange": record[6],
                "quantity": record[7],
                "turnoverBest": record[8],
                "totalTurnover": record[9]
            }
            for record in data
        ]
        response = requests.post(SPRING_API_URL_HISTORICAL, json=formatted_data)
        if response.status_code == 200:
            print(f"Successfully sent {len(formatted_data)} records to Spring API.")
        else:
            print(f"Failed to send data to Spring API: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to Spring API: {str(e)}")


def format_price(price_str):
    try:
        price_str = price_str.replace(",", "").replace(" ", "")
        price_float = float(price_str)
        return "{:,.2f}".format(price_float)
    except ValueError:
        return price_str


@app.route("/fetch_and_store_data", methods=["POST"])
def fetch_and_store_data():
    end_date = datetime.today()
    start_date = end_date.replace(year=end_date.year - 10, month=1, day=1)
    start_date_str = start_date.strftime("%m-%d-%Y")
    end_date_str = end_date.strftime("%m-%d-%Y")

    issuers = fetch_issuer_codes()
    if not issuers:
        return jsonify({"error": "No issuers found."}), 400

    chunk_size = 100
    total_issuers = len(issuers)

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for i in range(0, total_issuers, chunk_size):
            chunk = issuers[i:i + chunk_size]
            for issuer in chunk:
                issuer_code = issuer["code"]
                futures.append(executor.submit(fetch_and_parse_issuer_data, issuer_code, start_date_str, end_date_str))

        all_data = []
        for future in as_completed(futures):
            all_data.extend(future.result())

    sorted_data = sorted(all_data, key=lambda x: (x[0], -datetime.strptime(x[1], "%m/%d/%Y").timestamp()))

    send_data_to_spring_api(sorted_data)

    return jsonify({"message": "Data fetching and storage completed."}), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
