import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3



DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")


def fetch_issuers_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM issuers")
    issuers = cursor.fetchall()
    conn.close()
    return issuers

def scrape_data(issuer_code, from_date, to_date):
    url = 'https://www.mse.mk/mk/stats/symbolhistory/kmb'
    params = {
        'Code': issuer_code,
        'FromDate': from_date.strftime("%d.%m.%Y"),
        'ToDate': to_date.strftime("%d.%m.%Y")
    }

    response = requests.get(url, params=params)
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

    return data

# Function to get the last saved date for issuer
def get_last_date_from_db(cursor, publisher_code):
    cursor.execute("SELECT MAX(date) FROM historical_data WHERE issuer_code = ?", (publisher_code,))
    result = cursor.fetchone()
    return result[0] if result[0] else None

def main():

    issuers = fetch_issuers_from_db()

    issuers = issuers

    all_data = []  # List for scraped data

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now()

    # Iterate through each issuer
    for issuer_code, issuer_name in issuers:
        print(f"Fetching data for issuer: {issuer_name} ({issuer_code})")

        # Check the last saved date
        last_date = get_last_date_from_db(cursor, issuer_code)

        if last_date:
            last_date = datetime.strptime(last_date, '%Y-%m-%d')
            print(f"Last available data for {issuer_name} is up to {last_date.strftime('%Y-%m-%d')}.")
            start_date = last_date + timedelta(days=1)
        else:
            # If no data,start from 10 years ago
            start_date = today - timedelta(days=10 * 365)
            print(f"No existing data for {issuer_name}. Fetching data from {start_date.strftime('%Y-%m-%d')}.")


        if start_date > today:
            print(f"No new data needed for {issuer_name}. Already up to date.")
            continue

        # Iterate year by year and month by month
        for year in range(start_date.year, today.year + 1):
            for month in range(1, 13):
                from_date = datetime(year, month, 1)
                # Determine the last day of the month
                if month == 12:
                    to_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    to_date = datetime(year, month + 1, 1) - timedelta(days=1)


                if from_date < start_date:
                    continue

                #Fetch data for every month
                monthly_data = scrape_data(issuer_code, from_date, to_date)

                if monthly_data:

                    for row in monthly_data:
                        all_data.append((issuer_code, *row))


    conn.close()

    return all_data


if __name__ == "__main__":
    scraped_data = main()


