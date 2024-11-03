import os
import requests
from bs4 import BeautifulSoup
import sqlite3

# Define the database path relative to the script’s location
DB_PATH = os.path.join(os.path.dirname(__file__), "../database/macedonian_stock_exchange.db")

def fetch_issuers():
    url = "https://www.mse.mk/en/stats/symbolhistory/kmb"

    # Fetch page content
    response = requests.get(url)
    response.raise_for_status()

    # Parse page content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract issuer codes and names
    issuers = []
    for option in soup.select("#Code option"):  # Update with actual CSS selector
        code = option.get("value")
        name = option.text.strip()


        # Skip codes with numbers
        if not any(char.isdigit() for char in code) and not any(char.isdigit() for char in name):
            issuers.append((code, name))

    # Store issuers in the database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for code, name in issuers:
        cursor.execute("INSERT OR IGNORE INTO issuers (code, name) VALUES (?, ?)", (code, name))

    conn.commit()
    conn.close()
    print("Issuers fetched and stored in database.")

if __name__ == "__main__":
    fetch_issuers()
