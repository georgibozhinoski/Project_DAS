import pandas as pd
import numpy as np

def calculate_sma(data, column, window):

    return data[column].rolling(window=window).mean()

def calculate_ema(data, column, span):

    return data[column].ewm(span=span, adjust=False).mean()

def calculate_wma(data, column, window):

    weights = np.arange(1, window + 1)
    return data[column].rolling(window).apply(
        lambda prices: np.dot(prices, weights) / weights.sum(), raw=True
    )

def calculate_macd(data, column, short_span=12, long_span=26):

    short_ema = data[column].ewm(span=short_span, adjust=False).mean()
    long_ema = data[column].ewm(span=long_span, adjust=False).mean()
    return short_ema - long_ema

def calculate_hma(data, column, window):

    half_window = int(window / 2)
    sqrt_window = int(np.sqrt(window))

    wma_half = calculate_wma(data, column, half_window)
    wma_full = calculate_wma(data, column, window)
    hma = calculate_wma(data.assign(temp=2 * wma_half - wma_full), "temp", sqrt_window)

    return hma
