import sqlite3
from Indicators.MovingAverages import *
from Indicators.Oscillators import *
from concurrent.futures import ThreadPoolExecutor


class StockAnalyzer:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_all_issuers(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            query = "SELECT DISTINCT issuer_code FROM historical_data"
            cursor.execute(query)

            issuers = [row[0] for row in cursor.fetchall()]
            conn.close()

            return issuers

        except Exception as e:
            return []

    def get_data(self, issuer_code):

        try:
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT date,
                   last_price AS "Last Price",
                   max_price AS "Max Price",
                   min_price AS "Min Price",
                   avg_price AS "Avg Price",
                   quantity AS "Quantity"
            FROM historical_data
            WHERE issuer_code = ?
            ORDER BY date ASC
            """

            data = pd.read_sql_query(query, conn, params=(issuer_code,))
            conn.close()

            data['date'] = pd.to_datetime(data['date'])

            if len(data) < 10:
                return None

            price_cols = ['Last Price', 'Max Price', 'Min Price', 'Avg Price']
            for col in price_cols:
                data[col] = data[col].apply(lambda x: float(str(x).replace('.', '').replace(',', '.'))
                if pd.notna(x) and x != '' else 0.0)

            data['Quantity'] = data['Quantity'].apply(lambda x: float(str(x).replace('.', '').replace(',', '.'))
            if pd.notna(x) and x != '' else 0.0)

            return data

        except Exception as e:
            return None

    def analyze_issuer(self, issuer_code):

        try:
            data = self.get_data(issuer_code)
            if data is None:
                return None

            timeframes = {
                'Daily': 'D',
                'Weekly': 'W',
                'Monthly': 'M'
            }

            results = {}
            for name, timeframe in timeframes.items():
                df_indicators = self.calculate_all_indicators(data, timeframe)
                signals = self.generate_signals(df_indicators)

                results[name] = {
                    'indicators': df_indicators,
                    'signals': signals
                }

            return {issuer_code: results}

        except Exception as e:
            return None

    def calculate_all_indicators(self, data, timeframe='D'):

        df = data.copy()

        if timeframe == 'W':
            df = df.resample('W', on='date').agg({
                'Last Price': 'last',
                'Max Price': 'max',
                'Min Price': 'min',
                'Avg Price': 'mean',
                'Quantity': 'sum'
            }).dropna()
        elif timeframe == 'M':
            df = df.resample('ME', on='date').agg({
                'Last Price': 'last',
                'Max Price': 'max',
                'Min Price': 'min',
                'Avg Price': 'mean',
                'Quantity': 'sum'
            }).dropna()
        else:

            df = df.set_index('date').sort_index()

        df['SMA_20'] = calculate_sma(df, 'Last Price', 20)
        df['EMA_10'] = calculate_ema(df, 'Last Price', 10)
        df['WMA_30'] = calculate_wma(df, 'Last Price', 30)
        df['MACD'] = calculate_macd(df, 'Last Price')
        df['HMA_50'] = calculate_hma(df, 'Last Price', 50)

        df['RSI'] = calculate_rsi(df, 'Last Price')
        stoch = calculate_stochastic(df, 'Max Price', 'Min Price', 'Last Price')
        df['STOCH_K'] = stoch['K_line']
        df['STOCH_D'] = stoch['D_line']
        df['CCI'] = calculate_cci(df, 'Max Price', 'Min Price', 'Last Price')
        df['MOMENTUM'] = calculate_momentum(df, 'Last Price')
        df['WILLIAMS_R'] = calculate_williams_r(df, 'Max Price', 'Min Price', 'Last Price')

        return df

    def generate_signals(self, df):

        signals = pd.DataFrame(index=df.index)
        signals['date'] = df.index
        signals['price'] = df['Last Price']
        signals['signal'] = 'HOLD'

        signals.loc[df['SMA_20'] > df['EMA_10'], 'MA_trend'] = 'BULLISH'
        signals.loc[df['SMA_20'] < df['EMA_10'], 'MA_trend'] = 'BEARISH'

        signals.loc[df['MACD'] > 0, 'MACD_signal'] = 'BULLISH'
        signals.loc[df['MACD'] < 0, 'MACD_signal'] = 'BEARISH'

        signals.loc[df['RSI'] > 70, 'RSI_signal'] = 'OVERBOUGHT'
        signals.loc[df['RSI'] < 30, 'RSI_signal'] = 'OVERSOLD'

        signals.loc[(df['STOCH_K'] > 80) & (df['STOCH_D'] > 80), 'STOCH_signal'] = 'OVERBOUGHT'
        signals.loc[(df['STOCH_K'] < 20) & (df['STOCH_D'] < 20), 'STOCH_signal'] = 'OVERSOLD'

        signals.loc[df['CCI'] > 100, 'CCI_signal'] = 'OVERBOUGHT'
        signals.loc[df['CCI'] < -100, 'CCI_signal'] = 'OVERSOLD'

        buy_condition = (
                (signals['MA_trend'] == 'BULLISH') &
                (signals['MACD_signal'] == 'BULLISH') &
                ((signals['RSI_signal'] == 'OVERSOLD') |
                 (signals['STOCH_signal'] == 'OVERSOLD') |
                 (signals['CCI_signal'] == 'OVERSOLD'))
        )

        sell_condition = (
                (signals['MA_trend'] == 'BEARISH') &
                (signals['MACD_signal'] == 'BEARISH') &
                ((signals['RSI_signal'] == 'OVERBOUGHT') |
                 (signals['STOCH_signal'] == 'OVERBOUGHT') |
                 (signals['CCI_signal'] == 'OVERBOUGHT'))
        )

        signals.loc[buy_condition, 'signal'] = 'BUY'
        signals.loc[sell_condition, 'signal'] = 'SELL'

        return signals

    def save_results(self, results, output_dir='analysis_results'):

        import os
        from datetime import datetime

        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for issuer_code, timeframe_results in results.items():
            issuer_dir = os.path.join(output_dir, issuer_code)
            os.makedirs(issuer_dir, exist_ok=True)

            for timeframe, data in timeframe_results.items():
                signals_file = os.path.join(issuer_dir, f"{issuer_code}_{timeframe}_signals_{timestamp}.csv")
                data['signals'].to_csv(signals_file)

                indicators_file = os.path.join(issuer_dir, f"{issuer_code}_{timeframe}_indicators_{timestamp}.csv")
                data['indicators'].to_csv(indicators_file)


def main():
    db_path = '..\..\Домашна 1\database\macedonian_stock_exchange.db'

    analyzer = StockAnalyzer(db_path)

    issuers = analyzer.get_all_issuers()
    print(f"From {len(issuers)} issuers to analyze")

    all_results = {}
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(analyzer.analyze_issuer, issuer): issuer for issuer in issuers}

        for future in futures:
            issuer = futures[future]
            try:
                result = future.result()
                if result:
                    all_results.update(result)
            except Exception as e:
                print(f"Error processing {issuer}: {str(e)}")

    analyzer.save_results(all_results)


if __name__ == "__main__":
    main()
