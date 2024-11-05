import os
import time
import pandas as pd
import sqlite3
import logging
from datetime import datetime, timedelta
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)

project_dir = os.path.dirname(__file__)
download_directory = os.path.join(project_dir, 'downloads')
os.makedirs(download_directory, exist_ok=True)

DB_PATH = os.path.join(project_dir, "../database/macedonian_stock_exchange.db")


def fetch_issuers():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM issuers")
    issuers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return issuers


def download_excel(issuer_code, start_date, end_date, download_number):
    issuer_folder = os.path.join(download_directory, issuer_code)
    os.makedirs(issuer_folder, exist_ok=True)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": issuer_folder,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    attempts = 0
    max_attempts = 5  # Set a maximum number of attempts to avoid infinite loops

    try:
        while attempts < max_attempts:
            try:
                formatted_start = start_date.strftime("%m/%d/%Y")
                formatted_end = end_date.strftime("%m/%d/%Y")
                url = f"https://www.mse.mk/en/stats/symbolhistory/{issuer_code}?FromDate={formatted_start}&ToDate={formatted_end}"
                driver.get(url)

                WebDriverWait(driver, 5).until(  # Timeout (raboti i pobrzo)
                    EC.element_to_be_clickable((By.ID, "btnExport"))
                ).click()

                time.sleep(random.uniform(3, 6))  # DCA

                # Check if the file has been downloaded
                file_name = "Historical Data.xls"
                file_path = os.path.join(issuer_folder, file_name)

                if os.path.exists(file_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_file_name = f"{issuer_code}_Historical_Data_{download_number}_{timestamp}.xls"
                    new_file_path = os.path.join(issuer_folder, new_file_name)
                    os.rename(file_path, new_file_path)
                    logging.info(f"Excel file downloaded for {issuer_code} as {new_file_name}.")
                    return new_file_path
                else:
                    # logging.warning(f"File not found after attempt {attempts + 1}. Retrying...")
                    attempts += 1
                    time.sleep(random.uniform(4, 8))  # DCA
                    continue  # Refresh the page and try again

            except Exception as e:
                logging.error(f"An error occurred while downloading for {issuer_code}: {e}")
                attempts += 1
                time.sleep(random.uniform(4, 8))  # DCA
                continue

    finally:
        driver.quit()

    logging.error(f"Max attempts reached for {issuer_code}. Download failed.")
    return None


def is_html_file(file_path):
    with open(file_path, 'rb') as f:
        header = f.read(10)
    return header.startswith(b'<!DOCTYPE html') or b'<html' in header


def convert_xls_to_html(folder_path):
    """Convert .xls files to .html files by renaming them."""
    files = os.listdir(folder_path)
    for filename in files:
        if filename.strip().endswith('.xls'):
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, filename.replace('.xls', '.html'))
            os.rename(old_file_path, new_file_path)
            logging.info(f"Renamed {old_file_path} to {new_file_path}")


def read_html_file(file_path):
    try:
        # logging.info(f"Attempting to read HTML file: {file_path}") # debug
        tables = pd.read_html(file_path)
        if tables:
            df = tables[0]

            issuer_code = os.path.basename(os.path.dirname(file_path))
            issuer_name = issuer_code
            return parse_table(df, issuer_code, issuer_name)
        else:
            logging.warning(f"No tables found in {file_path}")
            return pd.DataFrame()
    except Exception as e:
        # logging.error(f"Error reading {file_path}: {e}") debug
        return pd.DataFrame()


def parse_table(df, issuer_code, issuer_name):
    """Parse the DataFrame to extract relevant trading data."""
    parsed_data = []
    for index, row in df.iterrows():
        if len(row) >= 9:  # Ensure there are enough columns
            try:
                parsed_data.append({
                    'date': row.iloc[0],
                    'last_price': str(row.iloc[1]).replace(',', ''),
                    'max_price': str(row.iloc[2]).replace(',', ''),
                    'min_price': str(row.iloc[3]).replace(',', ''),
                    'avg_price': str(row.iloc[4]).replace(',', ''),
                    'percent_change': float(row.iloc[5]),
                    'quantity': float(row.iloc[6]),
                    'turnover_best': str(row.iloc[7]).replace(',', ''),
                    'total_turnover': str(row.iloc[8]).replace(',', ''),
                    'issuer_code': issuer_code,
                    'issuer_name': issuer_name  # Use the issuer name extracted from the folder
                })
            except Exception as e:
                logging.error(f"Error processing row {index}: {e}")  # debug

    return pd.DataFrame(parsed_data)


def clean_data(df):
    df.dropna(inplace=True)
    return df


def insert_historical_data(cursor, df, issuer_code):
    if 'date' not in df.columns:
        # logging.warning("Column 'date' not found in DataFrame") # debug
        return

    for _, row in df.iterrows():
        try:
            cursor.execute('''INSERT OR IGNORE INTO historical_data (issuer_code, date, last_price, max_price, min_price, avg_price, percent_change, quantity, turnover_best, total_turnover)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (issuer_code, row['date'], row['last_price'], row['max_price'],
                            row['min_price'], row['avg_price'], row['percent_change'],
                            row['quantity'], row['turnover_best'], row['total_turnover']))
        except sqlite3.Error as e:
            logging.error(f"Error inserting historical data for {issuer_code} on {row['date']}: {e}")  # debug


def process_html_files(folder_path, db_path, issuer_code):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    files = os.listdir(folder_path)
    # logging.info(f"Files found in directory: {files}") # debug

    for filename in files:
        if filename.strip().endswith('.html'):
            file_path = os.path.join(folder_path, filename)
            logging.info(f"Processing {file_path}...")

            df = read_html_file(file_path)
            if not df.empty:
                df = clean_data(df)
                insert_historical_data(cursor, df, issuer_code)  # Use extracted issuer code ( folder name )
            else:
                logging.warning(f"No data found in {file_path}. Skipping...")

    conn.commit()
    conn.close()


def process_issuer(issuer, end_date):
    issuer_folder = os.path.join(download_directory, issuer)
    for year in range(10):
        start_date = end_date - timedelta(days=(year + 1) * 365)
        end_date_for_year = start_date + timedelta(days=364)
        download_count = year + 1
        file_path = download_excel(issuer, start_date, end_date_for_year, download_count)

        if file_path:
            convert_xls_to_html(os.path.dirname(file_path))
            issuer_code = os.path.basename(issuer_folder)
            process_html_files(os.path.dirname(file_path), DB_PATH, issuer_code)


def main():
    end_date = datetime.now()
    issuers = fetch_issuers()  # Get issuer codes from the database
    with ThreadPoolExecutor(max_workers=5) as executor:  # ( Threads mozhe i pobrzo ) dca
        futures = {executor.submit(process_issuer, issuer, end_date): issuer for issuer in issuers}
        for future in futures:
            try:
                future.result()  # Wait for the result
            except Exception as e:
                logging.error(f"An error occurred while processing issuer {futures[future]}: {e}")


if __name__ == "__main__":
    main()
