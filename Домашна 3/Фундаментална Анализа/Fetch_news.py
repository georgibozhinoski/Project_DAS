import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from textblob import TextBlob
import sqlite3

# Define the database path change*
DB_PATH = '../../Домашна 1/database/macedonian_stock_exchange.db'

# Fetch news function
def fetch_news():

    url_base = 'https://www.mse.mk/en/news/latest/'

    news_articles = []
    today = datetime.today()
    one_year_ago = today - timedelta(days=365)

    page_number = 1
    while True:
        # Fetch the content of the current page
        url = f'{url_base}{page_number}'
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page {page_number}. Status code: {response.status_code}")
            break

        soup = BeautifulSoup(response.content, 'html.parser')
        news_content = soup.find_all('div', class_='row')

        # If no news found on the page, stop the loop
        if not news_content:
            print(f"No news found on page {page_number}. Ending scraping.")
            break

        for item in news_content:
            date_tag = item.find('a')
            if date_tag:
                date_str = date_tag.text.strip()

                try:
                    news_date = datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    continue

                # Stop scraping if the news date is older than one year ago
                if news_date < one_year_ago:
                    print(f"Reached news older than a year: {news_date}. Ending scraping.")
                    return news_articles

                # Process the valid news articles
                headline_tag = item.find('b')
                headline = headline_tag.text.strip() if headline_tag else "No headline"

                news_body_tag = item.find('p', class_='news-headline')
                news_body = news_body_tag.text.strip() if news_body_tag else "No body"

                # Fetch the detailed news page to get the full body
                detailed_news_url = item.find('a', href=True)['href']
                if detailed_news_url:
                    full_body = fetch_full_body(detailed_news_url)

                    # Perform sentiment analysis
                    sentiment = analyze_sentiment(full_body)

                    # Check if the news article matches a company
                    matching_companies = check_company_in_news(full_body, headline)

                    # Save the article to the list
                    for company in matching_companies:
                        news_articles.append({
                            'date': news_date,
                            'headline': headline,
                            'body': full_body,
                            'sentiment': sentiment,
                            'company': company
                        })

        # Move to the next page
        page_number += 1

    return news_articles

# Fetch body of article
def fetch_full_body(news_url):
    base_url = 'https://www.mse.mk'

    # Ensure the URL is absolute
    if not news_url.startswith('http'):
        news_url = base_url + news_url

    response = requests.get(news_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extract the body text from the panel
        body_tag = soup.find('div', class_='panel-body')
        if body_tag:
            paragraphs = body_tag.find_all('p')
            full_body = ' '.join([p.text.strip() for p in paragraphs])
            return full_body
        else:
            return "No body content found."
    else:
        return "Failed to retrieve detailed news."


def analyze_sentiment(text):
    """Perform sentiment analysis using TextBlob."""
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity  # Returns a value between -1 (negative) and 1 (positive)

    if sentiment_score > 0:
        sentiment = 'positive'
    elif sentiment_score < 0:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return sentiment


def check_company_in_news(news_body, headline):
    """Check if any company name appears in the news body or headline."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all unique issuer names (or any other relevant information from your database)
    cursor.execute("SELECT DISTINCT issuer_code FROM historical_data")
    companies = [row[0] for row in cursor.fetchall()]
    conn.close()

    matching_companies = []
    for company in companies:
        if company.lower() in news_body.lower() or company.lower() in headline.lower():
            matching_companies.append(company)

    return matching_companies


def save_news_to_db(news_articles):
    """Save news articles into the company_news table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the company_news table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            title TEXT NOT NULL,
            news_text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            date_fetched TEXT NOT NULL
        )
    ''')

    # Insert each news article into the table
    for article in news_articles:
        # Convert datetime to string format to avoid deprecation warning
        date_str = article['date'].strftime('%Y-%m-%d %H:%M:%S')  # Format the date to a string

        # Insert data into the correct columns
        cursor.execute('''
            INSERT INTO company_news (company_name, title, news_text, sentiment, date_fetched) 
            VALUES (?, ?, ?, ?, ?)
        ''', (article['company'], article['headline'], article['body'], article['sentiment'], date_str))

    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def main():
    # Fetch the news
    news_articles = fetch_news()

    if news_articles:
        # Save the news to the database
        save_news_to_db(news_articles)
        print(f"Saved {len(news_articles)} news articles to the database.")
    else:
        print("No news articles to save.")


if __name__ == "__main__":
    main()
