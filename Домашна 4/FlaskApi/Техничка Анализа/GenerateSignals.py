from flask import Flask, jsonify, request
import requests
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import concurrent.futures
from collections import defaultdict

app = Flask(__name__)

HISTORICAL_DATA_API_URL = "http://localhost:8080/api/historicaldata"
SIGNALS_API_URL = "http://localhost:8080/api/signals/add"


class StockAnalyzer:
    def __init__(self):
        self.timeframes = {
            'Daily': 'D',
            'Weekly': 'W',
            'Monthly': 'M'
        }

    def calculate_sma(self, data: pd.Series, period: int) -> pd.Series:
        return data.rolling(window=period).mean()

    def calculate_ema(self, data: pd.Series, period: int) -> pd.Series:
        return data.ewm(span=period, adjust=False).mean()

    def calculate_macd(self, data: pd.Series) -> pd.Series:
        exp1 = data.ewm(span=12, adjust=False).mean()
        exp2 = data.ewm(span=26, adjust=False).mean()
        return exp1 - exp2

    def calculate_rsi(self, data: pd.Series, period: int = 14) -> pd.Series:
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series,
                             k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        return k, d

    def resample_data(self, df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        if timeframe not in ['D', 'W', 'M']:
            raise ValueError(f"Invalid timeframe: {timeframe}")
        numeric_columns = ['Last Price', 'Max Price', 'Min Price', 'Avg Price', 'Quantity']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        if timeframe == 'D':
            return df.set_index('date').sort_index()
        return df.resample(timeframe, on='date').agg({
            'Last Price': 'last',
            'Max Price': 'max',
            'Min Price': 'min',
            'Avg Price': 'mean',
            'Quantity': 'sum'
        }).dropna()

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        high = df['Max Price']
        low = df['Min Price']
        close = df['Last Price']
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def calculate_all_indicators(self, df: pd.DataFrame, timeframe: str = 'D') -> pd.DataFrame:
        df = self.resample_data(df, timeframe)
        df['SMA_20'] = self.calculate_sma(df['Last Price'], 20)
        df['EMA_10'] = self.calculate_ema(df['Last Price'], 10)
        df['MACD'] = self.calculate_macd(df['Last Price'])
        df['RSI'] = self.calculate_rsi(df['Last Price'])
        df['STOCH_K'], df['STOCH_D'] = self.calculate_stochastic(
            df['Max Price'], df['Min Price'], df['Last Price']
        )
        df['Volume_SMA_20'] = self.calculate_sma(df['Quantity'], 20)
        df['Price_Change'] = df['Last Price'].pct_change()
        df['ATR'] = self.calculate_atr(df)
        return df

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        signals = pd.DataFrame(index=df.index)
        signals['date'] = df.index
        signals['price'] = df['Last Price']

        signals['MA_trend'] = np.where(df['SMA_20'] > df['EMA_10'], 'BULLISH', 'BEARISH')
        signals['MACD_signal'] = np.where(df['MACD'] > 0, 'BULLISH', 'BEARISH')
        signals['RSI_signal'] = 'NEUTRAL'
        signals.loc[df['RSI'] > 70, 'RSI_signal'] = 'OVERBOUGHT'
        signals.loc[df['RSI'] < 30, 'RSI_signal'] = 'OVERSOLD'
        signals['volume_trend'] = np.where(df['Quantity'] > df['Volume_SMA_20'], 'HIGH', 'LOW')

        buy_conditions = (
                (signals['MA_trend'] == 'BULLISH') &
                (signals['MACD_signal'] == 'BULLISH') &
                (signals['RSI_signal'] == 'OVERSOLD') &
                (signals['volume_trend'] == 'HIGH')
        )

        sell_conditions = (
                (signals['MA_trend'] == 'BEARISH') &
                (signals['MACD_signal'] == 'BEARISH') &
                (signals['RSI_signal'] == 'OVERBOUGHT') &
                (signals['volume_trend'] == 'HIGH')
        )

        signals['signal'] = None

        signals.loc[buy_conditions, 'signal'] = 'BUY'
        signals.loc[sell_conditions, 'signal'] = 'SELL'

        signals = signals.dropna(subset=['signal'])

        return signals

    def send_signals_to_spring(self, signals: pd.DataFrame, issuer_code: str, timeframe: str) -> bool:
        try:

            valid_signals = signals.dropna(subset=['signal'])

            signals_data = [
                {
                    'issuerCode': issuer_code,
                    'timeframe': timeframe,
                    'signal': row['signal'],
                    'date': row['date'].strftime('%Y-%m-%d'),
                    'price': float(row['price']),
                    'maTrend': row['MA_trend'],
                    'macdSignal': row['MACD_signal'],
                    'rsiSignal': row['RSI_signal'],
                    'volumeTrend': row['volume_trend']
                }
                for _, row in valid_signals.iterrows()
            ]

            if not signals_data:
                print(f"No valid signals to send for {issuer_code} ({timeframe})")
                return True

            response = requests.post(SIGNALS_API_URL, json=signals_data)
            success = response.status_code == 200
            print(f"Signal save for {issuer_code} ({timeframe}): {'Success' if success else 'Failed'}")
            return success
        except Exception as e:
            print(f"Error sending signals: {str(e)}")
            return False


class BatchStockAnalyzer:
    def __init__(self):
        self.analyzer = StockAnalyzer()

    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = ['lastPrice', 'maxPrice', 'minPrice', 'avgPrice', 'quantity']
        renamed_columns = {
            'lastPrice': 'Last Price',
            'maxPrice': 'Max Price',
            'minPrice': 'Min Price',
            'avgPrice': 'Avg Price',
            'quantity': 'Quantity'
        }
        df = df.copy()
        df = df.rename(columns=renamed_columns)
        for col in numeric_columns:
            mapped_col = renamed_columns[col]
            if col in df.columns:
                try:
                    if df[col].dtype == object:
                        cleaned = df[col].astype(str).apply(lambda x: x.strip('$£€¥').replace(',', '').strip())
                        cleaned = cleaned.apply(lambda x: str(float(x) / 100) if x.endswith('%') else x)
                        df[mapped_col] = pd.to_numeric(cleaned, errors='coerce')
                        df[mapped_col] = df[mapped_col].fillna(method='ffill').fillna(method='bfill')
                        print(f"Successfully processed {col} -> {mapped_col}")
                        print(f"Sample values: {df[mapped_col].head()}")
                        print(f"Data type: {df[mapped_col].dtype}")
                except Exception as e:
                    print(f"Error processing {col}: {str(e)}")
                    df[mapped_col] = np.nan
        return df

    def get_all_historical_data(self) -> Dict[str, pd.DataFrame]:
        try:
            response = requests.get(HISTORICAL_DATA_API_URL)
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code}")
            data = response.json()
            if not data:
                raise Exception("Empty data received from API")
            all_data = pd.DataFrame(data)
            all_data['date'] = pd.to_datetime(all_data['date'], format='%m/%d/%Y', errors='coerce')
            all_data = all_data.dropna(subset=['date'])
            all_data = self.preprocess_data(all_data)
            required_columns = ['Last Price', 'Max Price', 'Min Price', 'Avg Price', 'Quantity']
            for col in required_columns:
                if col not in all_data.columns:
                    raise Exception(f"Missing required column: {col}")
            all_data = all_data.dropna(subset=required_columns, how='all')
            grouped_data = {}
            for issuer_code, group in all_data.groupby('issuerCode'):
                if len(group) >= 20:
                    grouped_data[issuer_code] = group.sort_values('date')
            return grouped_data
        except Exception as e:
            print(f"Error in get_all_historical_data: {str(e)}")
            return {}

    def _analyze_single_issuer(self, issuer_code: str, data: pd.DataFrame) -> Dict:
        try:
            required_columns = ['Last Price', 'Max Price', 'Min Price', 'Avg Price', 'Quantity']
            if not all(col in data.columns for col in required_columns):
                return {"error": "Missing required columns"}
            if data[required_columns].isna().any().any():
                data[required_columns] = data[required_columns].interpolate(method='linear')
            if len(data) < 20:
                return {"error": "Insufficient data points"}
            timeframe_results = {}
            signal_count = 0
            for name, timeframe in self.analyzer.timeframes.items():
                try:
                    df_indicators = self.analyzer.calculate_all_indicators(data.copy(), timeframe)
                    signals = self.analyzer.generate_signals(df_indicators)
                    if not signals.empty:
                        if not self.analyzer.send_signals_to_spring(signals, issuer_code, name):
                            print(f"Failed to save signals for {issuer_code} - {name}")
                            continue
                        signal_count += len(signals)
                        timeframe_results[name] = {
                            "last_signal": signals.iloc[-1].to_dict(),
                            "signal_count": len(signals),
                            "date_range": {
                                "start": signals.index[0].strftime('%Y-%m-%d'),
                                "end": signals.index[-1].strftime('%Y-%m-%d')
                            }
                        }
                except Exception as e:
                    print(f"Error analyzing {issuer_code} for {name}: {str(e)}")
                    continue
            if not timeframe_results:
                return {"error": "Failed to generate any valid signals"}
            return {
                "data": timeframe_results,
                "signal_count": signal_count
            }
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}

    def analyze_batch(self, max_workers: int = 4) -> Dict:
        try:
            grouped_data = self.get_all_historical_data()
            if not grouped_data:
                return {"error": "No data available for analysis"}
            results = defaultdict(dict)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_issuer = {
                    executor.submit(self._analyze_single_issuer, issuer_code, data): issuer_code
                    for issuer_code, data in grouped_data.items()
                }
                for future in concurrent.futures.as_completed(future_to_issuer):
                    issuer_code = future_to_issuer[future]
                    try:
                        result = future.result()
                        results[issuer_code] = result
                    except Exception as e:
                        print(f"Error analyzing issuer {issuer_code}: {str(e)}")
                        results[issuer_code] = {"error": f"Failed to analyze issuer {issuer_code}"}
            return results
        except Exception as e:
            print(f"Error during batch analysis: {str(e)}")
            return {"error": f"Batch analysis failed: {str(e)}"}


@app.route('/analyze_all', methods=['GET'])
def analyze_all_data():
    try:
        max_workers = int(request.args.get('max_workers', 4))
        analyzer = BatchStockAnalyzer()
        results = analyzer.analyze_batch(max_workers=max_workers)
        if isinstance(results, dict) and results.get("errors"):
            print("Processing errors:", results["errors"])
        return jsonify(results), 200 if not results.get("errors") else 207
    except Exception as e:
        import traceback
        error_details = {
            "error": "Failed to process data",
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        print("Error details:", error_details)
        return jsonify(error_details), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
