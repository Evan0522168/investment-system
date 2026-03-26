import requests
import pandas as pd


def get_twse_stock_list():

    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"

    r = requests.get(url)

    data = r.json()

    df = pd.DataFrame(data)

    df.rename(columns={
        "Code": "Symbol",
        "Name": "Name"
    }, inplace=True)

    return df[["Symbol", "Name"]]