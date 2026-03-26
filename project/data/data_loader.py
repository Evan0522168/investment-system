from .symbol_resolver import resolve_market
from .yf_source import download_yf
from .twse_price import download_twse
from .cache import is_cache_valid, load_cache, save_cache, update_cache


def download_data(symbol, force_refresh=False):
    market = resolve_market(symbol)
    stock_id = symbol.replace(".TW", "")

    # 檢查快取
    if not force_refresh and is_cache_valid(stock_id):
        df = load_cache(stock_id)
        if df is not None:
            return df

    print(f"  [下載] 從網路下載 {stock_id} 資料...")

    # 下載新資料
    if market == "YF":
        df_new = download_yf(symbol)
    elif market == "TWSE":
        df_new = download_twse(stock_id)
    else:
        raise ValueError("Unknown market")

    # 合併或儲存快取
    df_old = load_cache(stock_id)
    if df_old is not None:
        df = update_cache(stock_id, df_old, df_new)
    else:
        save_cache(stock_id, df_new)
        df = df_new

    return df
