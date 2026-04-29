import yfinance as yf
import pandas as pd


def download_yf(symbol, start="2015-01-01", end=None):
    df = yf.download(symbol, start=start, end=end)
    if df.empty:
        raise ValueError(f"No data for {symbol}")
    if isinstance(df["Close"], pd.DataFrame):
        df["Close"] = df["Close"].squeeze()
    df = df.ffill()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df
