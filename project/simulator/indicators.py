import pandas as pd
import numpy as np


def calc_sma(series, period):
    return series.rolling(window=period).mean()


def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def calc_macd(series, fast=12, slow=26, signal=9):
    ema_fast = calc_ema(series, fast)
    ema_slow = calc_ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calc_ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calc_bollinger(series, period=20, num_std=2):
    sma = calc_sma(series, period)
    std = series.rolling(window=period).std()
    upper = sma + num_std * std
    lower = sma - num_std * std
    return upper, sma, lower


def calc_stochastic(df, k_period=14, d_period=3):
    lowest_low = df["Low"].rolling(window=k_period).min()
    highest_high = df["High"].rolling(window=k_period).max()
    k = 100 * (df["Close"] - lowest_low) / (highest_high - lowest_low)
    d = k.rolling(window=d_period).mean()
    return k, d


def calc_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def calc_obv(df):
    direction = df["Close"].diff().apply(
        lambda x: 1 if x > 0 else (-1 if x < 0 else 0)
    )
    return (direction * df["Volume"]).cumsum()


def calc_vwap(df):
    typical_price = (df["High"] + df["Low"] + df["Close"]) / 3
    return (typical_price * df["Volume"]).cumsum() / df["Volume"].cumsum()


def calc_sd(series, period):
    return series.rolling(window=period).std()


def calc_mean(series, period):
    return series.rolling(window=period).mean()


def calc_variance(series, period):
    return series.rolling(window=period).var()


def calc_zscore(series, period):
    mean = calc_mean(series, period)
    std = calc_sd(series, period)
    return (series - mean) / std


def calc_percentile(series, period):
    def pct_rank(x):
        return pd.Series(x).rank(pct=True).iloc[-1] * 100
    return series.rolling(window=period).apply(pct_rank, raw=True)


def calc_skewness(series, period):
    return series.rolling(window=period).skew()


def calc_momentum(series, period):
    return series.pct_change(periods=period) * 100


def calc_price_change_pct(series, period=1):
    return series.pct_change(periods=period) * 100


def calc_volume_change_pct(series, period=1):
    return series.pct_change(periods=period) * 100


def calc_rolling_correlation(series1, series2, period):
    return series1.rolling(window=period).corr(series2)


def calc_price_sd_ratio(series, period):
    sd = calc_sd(series, period)
    return series / sd


def get_indicator_value(df, source_config):
    """
    Universal indicator calculator for Advanced Builder
    source_config example:
    {
        "source": "RSI",
        "period": 14,
        "period2": 3,
        "value": 30
    }
    """
    source = source_config.get("source", "Close")
    period = int(source_config.get("period", 14))
    period2 = int(source_config.get("period2", 3))
    close = df["Close"]

    if source == "Close":
        return close
    elif source == "Open":
        return df["Open"]
    elif source == "High":
        return df["High"]
    elif source == "Low":
        return df["Low"]
    elif source == "Volume":
        return df["Volume"]
    elif source == "SMA":
        return calc_sma(close, period)
    elif source == "EMA":
        return calc_ema(close, period)
    elif source == "RSI":
        return calc_rsi(close, period)
    elif source == "MACD_Line":
        macd, _, _ = calc_macd(close)
        return macd
    elif source == "MACD_Signal":
        _, signal, _ = calc_macd(close)
        return signal
    elif source == "MACD_Histogram":
        _, _, hist = calc_macd(close)
        return hist
    elif source == "Bollinger_Upper":
        upper, _, _ = calc_bollinger(close, period)
        return upper
    elif source == "Bollinger_Middle":
        _, mid, _ = calc_bollinger(close, period)
        return mid
    elif source == "Bollinger_Lower":
        _, _, lower = calc_bollinger(close, period)
        return lower
    elif source == "Stoch_K":
        k, _ = calc_stochastic(df, period, period2)
        return k
    elif source == "Stoch_D":
        _, d = calc_stochastic(df, period, period2)
        return d
    elif source == "ATR":
        return calc_atr(df, period)
    elif source == "VWAP":
        return calc_vwap(df)
    elif source == "SD":
        return calc_sd(close, period)
    elif source == "Mean":
        return calc_mean(close, period)
    elif source == "Variance":
        return calc_variance(close, period)
    elif source == "ZScore":
        return calc_zscore(close, period)
    elif source == "Percentile":
        return calc_percentile(close, period)
    elif source == "Skewness":
        return calc_skewness(close, period)
    elif source == "Momentum":
        return calc_momentum(close, period)
    elif source == "Price_Change_Pct":
        return calc_price_change_pct(close, period)
    elif source == "Volume_Change_Pct":
        return calc_volume_change_pct(df["Volume"], period)
    elif source == "Price_SD_Ratio":
        return calc_price_sd_ratio(close, period)
    else:
        return close
