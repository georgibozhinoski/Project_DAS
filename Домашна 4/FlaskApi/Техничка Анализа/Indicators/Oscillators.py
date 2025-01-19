import pandas as pd
import numpy as np


def calculate_rsi(data, column, period=14):
    delta = data[column].diff()
    gain = (delta.where(delta > 0, 0))
    loss = (-delta.where(delta < 0, 0))
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_stochastic(data, high_col, low_col, close_col, k_period=14, d_period=3):
    lowest_low = data[low_col].rolling(window=k_period).min()
    highest_high = data[high_col].rolling(window=k_period).max()
    k_line = 100 * ((data[close_col] - lowest_low) / (highest_high - lowest_low))

    d_line = k_line.rolling(window=d_period).mean()

    return pd.DataFrame({
        'K_line': k_line,
        'D_line': d_line
    })


def calculate_cci(data, high_col, low_col, close_col, period=20):
    tp = (data[high_col] + data[low_col] + data[close_col]) / 3
    sma_tp = tp.rolling(window=period).mean()
    mad = tp.rolling(window=period).apply(lambda x: np.abs(x - x.mean()).mean())
    cci = (tp - sma_tp) / (0.015 * mad)

    return cci


def calculate_momentum(data, column, period=14):
    return data[column].diff(period)


def calculate_williams_r(data, high_col, low_col, close_col, period=14):
    highest_high = data[high_col].rolling(window=period).max()
    lowest_low = data[low_col].rolling(window=period).min()
    williams_r = -100 * ((highest_high - data[close_col]) / (highest_high - lowest_low))

    return williams_r
