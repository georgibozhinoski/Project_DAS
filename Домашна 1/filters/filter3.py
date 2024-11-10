import os
import sqlite3
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from .filter2 import *

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")


def fetch_missing_data(issuer_code, last_available_date, end_date):
    start_date = last_available_date + timedelta(days=1) if last_available_date else end_date - timedelta(days=3650)
   # print(
    #    f"Fetching data for issuer {issuer_code} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    # Fetch and parse the data from the server
    missing_data = fetch_and_parse_issuer_data(issuer_code, start_date, end_date)

    #if missing_data:
     #   print(f"Fetched {len(missing_data)} records for {issuer_code}")
    #else:
     #   print(f"No new data fetched for {issuer_code}")

    return missing_data


def update_issuer_data():
    end_date = datetime.today()
    print(f"Current date: {end_date.strftime('%Y-%m-%d')}")

    issuer_codes = fetch_issuer_codes()
    print(f"Found {len(issuer_codes)} issuers to check.")


    all_missing_data = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        future_to_issuer = {
            executor.submit(fetch_issuer_data, issuer_code, end_date): issuer_code
            for issuer_code in issuer_codes
        }

        for future in as_completed(future_to_issuer):
            issuer_code = future_to_issuer[future]
            try:
                missing_data = future.result()
                if missing_data:
                    all_missing_data.extend(missing_data)
            except Exception as exc:
                print(f"Error fetching data for {issuer_code}: {exc}")

    if all_missing_data:
        all_missing_data = sort_and_format_data(all_missing_data)
        print(f"Sorted and formatted {len(all_missing_data)} records.")

        # Insert the new data into the database in bulk
        insert_data_into_db_bulk(all_missing_data)
        print(f"Inserted {len(all_missing_data)} new records.")
    else:
        print("No new data to insert.")

    sort_database()


def fetch_issuer_data(issuer_code, end_date):
    last_available_date = fetch_last_available_date(issuer_code)
    if last_available_date:
       # print(f"Last available date for {issuer_code}: {last_available_date.strftime('%Y-%m-%d')}")
        if last_available_date < end_date:
            return fetch_missing_data(issuer_code, last_available_date, end_date)
    else:
        #print(f"No data found for issuer {issuer_code}, fetching from 10 years ago.")
        return fetch_missing_data(issuer_code, None, end_date)


def format_price(price):
    if price is None:
        return None  # Return None if price is None

    # print(f"Original price: {price} (Type: {type(price)})")

    try:
        price = float(price)  # Ensure price is treated as a float
        return f"{price:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        # Handle the case where the price can't be converted to a float
        print(f"Failed to convert price: {price} to float")
        return None  # Return None if conversion fails


def clean_price(price):
    if price is None:
        return None
    try:
        cleaned_price = ''.join(c for c in str(price) if c.isdigit() or c == '.')
        return float(cleaned_price) if cleaned_price else None
    except ValueError:
        return None


def sort_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA foreign_keys = ON;")

        cursor.execute(""" 
            CREATE INDEX IF NOT EXISTS idx_issuer_code_date ON historical_data (issuer_code, date DESC);
        """)

        # Fetch all the data and format the prices
        cursor.execute("SELECT * FROM historical_data")
        all_data = cursor.fetchall()

        formatted_data = []
        for record in all_data:
            formatted_record = {
                "id": record[0],
                "issuer_code": record[1],
                "date": record[2],
                "last_price": format_price(clean_price(record[3])),
                "max_price": format_price(clean_price(record[4])),
                "min_price": format_price(clean_price(record[5])),
                "avg_price": format_price(clean_price(record[6])),
                "percent_change": record[7],
                "quantity": record[8],
                "turnover_best": record[9],
                "total_turnover": record[10]
            }
            formatted_data.append(formatted_record)

        cursor.execute("DELETE FROM historical_data")
        cursor.executemany("""
            INSERT INTO historical_data (id, issuer_code, date, last_price, max_price, min_price, avg_price, percent_change, quantity, turnover_best, total_turnover)
            VALUES (:id, :issuer_code, :date, :last_price, :max_price, :min_price, :avg_price, :percent_change, :quantity, :turnover_best, :total_turnover)
        """, formatted_data)

        conn.commit()

    except sqlite3.Error as e:
        print(f"Error while sorting and formatting database: {e}")
    finally:
        conn.close()


def main():
    update_issuer_data()


if __name__ == "__main__":
    main()
