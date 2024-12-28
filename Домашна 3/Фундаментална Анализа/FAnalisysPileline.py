import sqlite3
import pandas as pd
import os
import subprocess
import sys
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

#Base
class FundamentalAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path
        self.analyzer = SentimentIntensityAnalyzer()
#Hist data
    def get_historical_data(self, issuer_code):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT date, percent_change, quantity, total_turnover
            FROM historical_data
            WHERE issuer_code = ?
            ORDER BY date ASC
            """
            data = pd.read_sql_query(query, conn, params=(issuer_code,))
            conn.close()

            # Convert 'date' to datetime format
            data['date'] = pd.to_datetime(data['date'], errors='coerce')

            # Handle invalid or missing numerical data by setting them as NaN
            data['percent_change'] = pd.to_numeric(data['percent_change'], errors='coerce')
            data['quantity'] = pd.to_numeric(data['quantity'], errors='coerce')
            data['total_turnover'] = pd.to_numeric(data['total_turnover'], errors='coerce')

            # Drop rows with NaN values in critical columns
            data.dropna(subset=['percent_change', 'quantity', 'total_turnover'], inplace=True)

            return data

        except Exception as e:
            print(f"Error fetching historical data for {issuer_code}: {str(e)}")
            return None
# Get issuers
    def get_all_issuers(self):

        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT DISTINCT issuer_code FROM historical_data"
            issuers = pd.read_sql_query(query, conn)
            conn.close()
            return issuers['issuer_code'].tolist()
        except Exception as e:
            print(f"Error fetching issuers: {str(e)}")
            return []
# Get company news
    def get_company_news(self, issuer_code):
        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT title, news_text, sentiment
            FROM company_news
            WHERE company_name = ?
            """
            news_data = pd.read_sql_query(query, conn, params=(issuer_code,))
            conn.close()
            return news_data  # This returns a DataFrame
        except Exception as e:
            print(f"Error fetching company news for {issuer_code}: {str(e)}")
            return []
# Analysis with historical data and news article
    def analyze_issuer(self, issuer_code, news_url=None):
        try:
            # Fetch historical data
            historical_data = self.get_historical_data(issuer_code)
            if historical_data is None or historical_data.empty:
                print(f"No historical data for {issuer_code}")
                return None

            # Fetch related news data
            company_news = self.get_company_news(issuer_code)

            # Analyze sentiment from company news articles
            news_sentiment = 'N/A'
            recommendation = 'Следи ситуацијата'

            if not company_news.empty:
                for _, news_item in company_news.iterrows():
                    news_text = news_item['title'] + " " + news_item['news_text']
                    sentiment = self.get_sentiment(news_text)
                    recommendation = self.stock_recommendation(sentiment)
                    news_sentiment = sentiment
            else:
                historical_avg_percent_change = historical_data['percent_change'].mean()

                # Determine sentiment based on historical data
                if historical_avg_percent_change > 0:
                    news_sentiment = 'positive'
                    recommendation = 'Купи акции'
                elif historical_avg_percent_change < 0:
                    news_sentiment = 'negative'
                    recommendation = 'Продади акции'
                else:
                    news_sentiment = 'neutral'
                    recommendation = 'Следи ситуацијата'

            # Summarize historical data
            historical_summary = {
                'average_percent_change': historical_data['percent_change'].mean(),
                'total_quantity': historical_data['quantity'].sum(),
                'total_turnover': historical_data['total_turnover'].sum()
            }

            results = {
                'issuer_code': issuer_code,
                'historical_summary': historical_summary,
                'news_sentiment': news_sentiment,
                'recommendation': recommendation
            }

            return results

        except Exception as e:
            print(f"Error analyzing issuer {issuer_code}: {str(e)}")
            return None
        # Sentiment
    def get_sentiment(self, text):
        sentiment_score = self.analyzer.polarity_scores(text)
        if sentiment_score['compound'] >= 0.05:
            return 'positive'
        elif sentiment_score['compound'] <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    def stock_recommendation(self, sentiment):
        if sentiment == 'positive':
            return 'Купи акции'
        elif sentiment == 'negative':
            return 'Продади акции'
        else:
            return 'Следи ситуацијата'

    def save_results(self, results, output_dir='fundamental_analysis_results'):
        try:
            os.makedirs(output_dir, exist_ok=True)

            for issuer_code, result in results.items():
                issuer_dir = os.path.join(output_dir, issuer_code)
                os.makedirs(issuer_dir, exist_ok=True)

                historical_summary = result['historical_summary']

                # Create DataFrame for historical summary
                historical_df = pd.DataFrame([historical_summary])
                historical_file = os.path.join(issuer_dir, f"{issuer_code}_historical_summary.csv")
                historical_df.to_csv(historical_file, index=False)

                # Save sentiment and recommendation
                sentiment_file = os.path.join(issuer_dir, f"{issuer_code}_sentiment_recommendation.csv")
                sentiment_df = pd.DataFrame([{
                    'sentiment': result['news_sentiment'],
                    'recommendation': result['recommendation']
                }])
                sentiment_df.to_csv(sentiment_file, index=False)

                print(f"Results for {issuer_code} saved to {issuer_dir}")
        except Exception as e:
            print(f"Error saving results: {str(e)}")
    #Before run fetch news update company_news table
    def run_fetch_news(self):

        try:
            result = subprocess.run([sys.executable, 'Fetch_news.py'], check=True)
            print("Fetch_news.py executed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error executing Fetch_news.py: {e}")
            return False


def main():
    db_path = r'E:\Predmeti Faks\Das_Project\Project_DAS\Домашна 1\database\macedonian_stock_exchange.db'
    analyzer = FundamentalAnalyzer(db_path)

    # Run Fetch_news.py to update company news data
    if not analyzer.run_fetch_news():
        print("Failed to update company news. Exiting.")
        return

    # Get all issuers from the database
    issuers = analyzer.get_all_issuers()
    print(f"Found {len(issuers)} issuers to analyze")

    all_results = {}

    news_url = 'https://seinet.com.mk/'

    for issuer in issuers:
        #Perform analysis with optional analysis
        result = analyzer.analyze_issuer(issuer, news_url)
        if result:
            all_results[issuer] = result

    #Save all results into individual CSV files
    analyzer.save_results(all_results)


if __name__ == "__main__":
    main()


