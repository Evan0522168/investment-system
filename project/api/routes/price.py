import requests
import pandas as pd
import urllib3
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_twse_month(stock_id, date):
    url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
    params = {
        "response": "json",
        "date": date,
        "stockNo": stock_id
    }
    try:
        r = requests.get(url, params=params, timeout=10, verify=False)
        data = r.json()
        if data["stat"] != "OK":
            print(f"  [TWSE] {stock_id} {date}: stat={data['stat']}")
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
        print(f"  [TWSE] {stock_id} {date}: {len(df)} rows")
        return df
    except Exception as e:
        print(f"  [TWSE] {stock_id} {date}: ERROR {e}")
        return None


def download_twse(stock_id, start_year=2020):
    dfs = []
    today = datetime.today()
    print(f"  [TWSE] Starting download for {stock_id} from {start_year}")
    for year in range(start_year, today.year + 1):
        for month in range(1, 13):
            if year == today.year and month > today.month:
                break
            date = f"{year}{month:02d}01"
            df = fetch_twse_month(stock_id, date)
            if df is not None:
                dfs.append(df)
    print(f"  [TWSE] Total months fetched: {len(dfs)}")
    if not dfs:
        raise ValueError("No TWSE data found")
    result = pd.concat(dfs)
    result = result[~result.index.duplicated()]
    result.sort_index(inplace=True)
    return result
