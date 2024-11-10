import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("macedonian_stock_exchange.db")
cursor = conn.cursor()

# Create table for issuers
cursor.execute('''
CREATE TABLE IF NOT EXISTS issuers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL
)
''')

# Create table for historical data
cursor.execute('''
CREATE TABLE IF NOT EXISTS historical_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issuer_code TEXT NOT NULL,
    date TEXT,
    last_price TEXT,
    max_price TEXT,
    min_price TEXT,
    avg_price TEXT,
    percent_change TEXT,
    quantity TEXT,
    turnover_best TEXT,
    total_turnover TEXT,
    FOREIGN KEY (issuer_code) REFERENCES issuers (code),
    UNIQUE(issuer_code, date)
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()
