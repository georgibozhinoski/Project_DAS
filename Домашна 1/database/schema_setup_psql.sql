-- Schema for PostgreSQL Database: Macedonian Stock Exchange

-- Create table for issuers
CREATE TABLE IF NOT EXISTS issuers (
    id SERIAL PRIMARY KEY,          -- Auto-incrementing primary key
    code TEXT UNIQUE NOT NULL,      -- Unique issuer code
    name TEXT NOT NULL              -- Name of the issuer
);

-- Create table for historical data
CREATE TABLE IF NOT EXISTS historical_data (
    id SERIAL PRIMARY KEY,              -- Auto-incrementing primary key
    issuer_code TEXT NOT NULL,          -- Foreign key linking to issuers(code)
    date DATE NOT NULL,                 -- Date of the historical record
    last_price NUMERIC(12, 2),          -- Last price of the stock
    max_price NUMERIC(12, 2),           -- Maximum price of the stock
    min_price NUMERIC(12, 2),           -- Minimum price of the stock
    avg_price NUMERIC(12, 2),           -- Average price of the stock
    percent_change NUMERIC(6, 2),       -- Percent change in the stock price
    quantity BIGINT,                    -- Quantity of stocks traded
    turnover_best NUMERIC(18, 2),       -- Best turnover value
    total_turnover NUMERIC(18, 2),      -- Total turnover value
    FOREIGN KEY (issuer_code) REFERENCES issuers (code) ON DELETE CASCADE, -- Ensures referential integrity
    UNIQUE (issuer_code, date)          -- Ensures unique records per issuer and date
);
CREATE TABLE IF NOT EXISTS company_news (
            id SERIAL PRIMARY KEY ,
            company_name TEXT NOT NULL,
            title TEXT NOT NULL,
            news_text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            date_fetched TEXT NOT NULL
);

-- Add indexes for optimized queries
CREATE INDEX IF NOT EXISTS idx_historical_data_issuer_date
ON historical_data (issuer_code, date);

-- Add an index for quick lookups of issuers by code
CREATE INDEX IF NOT EXISTS idx_issuers_code
ON issuers (code);
