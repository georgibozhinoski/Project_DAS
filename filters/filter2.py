import os
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import sqlite3



DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")


async def fetch_issuers_from_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM issuers")
    issuers = cursor.fetchall()
    conn.close()
    return issuers

async def scrape_data(session,issuer_code, from_date, to_date):
    url = f'https://www.mse.mk/mk/stats/symbolhistory/{issuer_code}'
    params = {
        'Code': issuer_code,
        'FromDate': from_date.strftime("%d.%m.%Y"),
        'ToDate': to_date.strftime("%d.%m.%Y")
    }

    async with session.get(url, params=params) as response:
        response.raise_for_status()
        soup = BeautifulSoup(await response.text(), 'html.parser')
        data = []

    # Table Selector for data
    table = soup.find('table', {'id': 'resultsTable'})

    if table:
        for row in table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if cols:
                row_data = [col.text.strip() for col in cols]
                data.append(row_data)
    # print(data) #test
    return data

# Function to get the last saved date for issuer
async def get_last_date_from_db(cursor, publisher_code):
    cursor.execute("SELECT MAX(date) FROM historical_data WHERE issuer_code = ?", (publisher_code,))
    result = cursor.fetchone()
    return result[0] if result[0] else None
async def fetch_data_for_issuer(session, issuer_code, issuer_name, start_date, today):
    all_data = []
    print(f"Fetching data for issuer: {issuer_name} ({issuer_code})")

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

            # Fetch data for every month
            try:
                monthly_data = await scrape_data(session, issuer_code, from_date, to_date)
                if monthly_data:
                    for row in monthly_data:
                        all_data.append((issuer_code, *row))
                   # print(all_data) #for testing
            except Exception as e:
                print(f"Error fetching data for {issuer_name} ({issuer_code}) from {from_date} to {to_date}: {e}")

    return all_data
async def main():

    issuers = await fetch_issuers_from_db()

    today = datetime.now()
    all_data = []  # List for all scraped data

    # Create a session for aiohttp
    async with aiohttp.ClientSession() as session:
        # Prepare a list for futures
        futures = []
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Iterate through each issuer to prepare for concurrent scraping
        for issuer_code, issuer_name in issuers:
            last_date = await get_last_date_from_db(cursor, issuer_code)

            if last_date:
                last_date = datetime.strptime(last_date, '%Y-%m-%d')
                print(f"Last available data for {issuer_name} is up to {last_date.strftime('%Y-%m-%d')}.")
                start_date = last_date + timedelta(days=1)
            else:
                # If no data, start from 10 years ago
                start_date = today - timedelta(days=10 * 365)
                print(f"No existing data for {issuer_name}. Fetching data from {start_date.strftime('%Y-%m-%d')}.")

            if start_date > today:
                print(f"No new data needed for {issuer_name}. Already up to date.")
                continue

            # Fetch data for the issuer
            futures.append(fetch_data_for_issuer(session, issuer_code, issuer_name, start_date, today))

        # Collect results
        results = await asyncio.gather(*futures)
        for result in results:
            all_data.extend(result)

    conn.close()
    return all_data


if __name__ == "__main__":
    scraped_data = asyncio.run(main())



