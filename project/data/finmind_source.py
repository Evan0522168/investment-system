import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_finmind(stock_id, start="2020-01-01"):
    print(f"  [FinMind] Downloading {stock_id} from {start}...")
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockPrice",
        "data_id": stock_id,
        "start_date": start,
        "token": ""  # 不需要 token 也可以用，有限制但夠用
    }
    try:
        r = requests.get(url, params=params, timeout=30, verify=False)
        data = r.json()
        if data["status"] != 200:
            raise ValueError(f"FinMind error: {data['msg']}")
        df = pd.DataFrame(data["data"])
        if df.empty:
            raise ValueError(f"No data for {stock_id}")
        df["Date"] = pd.to_datetime(df["date"])
        df.set_index("Date", inplace=True)
        df.rename(columns={
            "open": "Open",
            "max": "High",
            "min": "Low",
            "close": "Close",
            "Trading_Volume": "Volume"
        }, inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df.sort_index()
        print(f"  [FinMind] Success: {len(df)} rows")
        return df
    except Exception as e:
        print(f"  [FinMind] ERROR: {e}")
        raise ValueError(f"No data for {stock_id}: {e}")
