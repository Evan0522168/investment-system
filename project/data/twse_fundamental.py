import requests
import pandas as pd


def fetch_twse_fundamental():

    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"

    r = requests.get(url)

    data = r.json()

    df = pd.DataFrame(data)

    df.rename(columns={
        "Code": "Symbol",
        "Name": "Name",
        "PEratio": "PE",
        "DividendYield": "DividendYield",
        "PBratio": "PB"
    }, inplace=True)

    return df