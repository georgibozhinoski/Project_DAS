import os
import requests
from bs4 import BeautifulSoup
import sqlite3
import psycopg2
from db_params import DB_PARAMS

def fetch_issuers():
    url = "https://www.mse.mk/en/stats/symbolhistory/kmb"

    # Fetch page content
    response = requests.get(url)
    response.raise_for_status()

    # Parse page content with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract issuer codes and names
    issuers = []
    for option in soup.select("#Code option"):
        code = option.get("value")
        name = option.text.strip()


        # Skip codes with numbers
        if not any(char.isdigit() for char in code) and not any(char.isdigit() for char in name):
            issuers.append((code, name))

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cursor = conn.cursor()

        # Insert issuers into the database
        for code, name in issuers:
            cursor.execute("""
                   INSERT INTO issuers (code, name) 
                   VALUES (%s, %s)
                   ON CONFLICT (code) DO NOTHING
               """, (code, name))

        conn.commit()
        print("Issuers fetched and stored in the database.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
            if conn:
                cursor.close()
                conn.close()
if __name__ == "__main__":
    fetch_issuers()