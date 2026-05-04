import requests
import pandas as pd
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_twse_fundamental():
    url = "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL"
    r = requests.get(url, verify=False)
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
