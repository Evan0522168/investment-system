import requests
import pandas as pd
from datetime import datetime


def fetch_twse_month(stock_id, date):
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {
        "response": "json",
        "date": date,
        "stockNo": stock_id
    }
    r = requests.get(url, params=params)
    data = r.json()
    if data["stat"] != "OK":
        return None
    df = pd.DataFrame(data["data"], columns=data["fields"])
    df.rename(columns={
        "日期": "Date",
        "開盤價": "Open",
        "最高價": "High",
        "最低價": "Low",
        "收盤價": "Close",
        "成交股數": "Volume"
    }, inplace=True)
    df["Date"] = pd.to_datetime(df["Date"].apply(
        lambda x: f"{int(x.split('/')[0]) + 1911}/{x.split('/')[1]}/{x.split('/')[2]}"
    ))
    df.set_index("Date", inplace=True)
    for col in ["Open", "High", "Low", "Close"]:
        df[col] = df[col].str.replace(",", "").astype(float)
    df["Volume"] = df["Volume"].str.replace(",", "").astype(float)
    return df


def download_twse(stock_id, start_year=2015):
    dfs = []
    today = datetime.today()
    for year in range(start_year, today.year + 1):
        for month in range(1, 13):
            if year == today.year and month > today.month:
                break
            date = f"{year}{month:02d}01"
            try:
                df = fetch_twse_month(stock_id, date)
                if df is not None:
                    dfs.append(df)
            except Exception:
                continue
    if not dfs:
        raise ValueError("No TWSE data found")
    result = pd.concat(dfs)
    result = result[~result.index.duplicated()]
    result.sort_index(inplace=True)
    return result
