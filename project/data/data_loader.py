from .symbol_resolver import resolve_market
from .yf_source import download_yf
from .finmind_source import download_finmind
from .supabase_cache import is_cache_valid, load_cache, save_cache, update_cache


def download_data(symbol, force_refresh=False, start_year=2020):
    # 判斷市場
    if symbol.isdigit():
        market = "TW"
        stock_id = symbol
        yf_symbol = f"{symbol}.TW"
    elif symbol.endswith(".TW"):
        market = "TW"
        stock_id = symbol.replace(".TW", "")
        yf_symbol = symbol
    else:
        market = "YF"
        stock_id = symbol
        yf_symbol = symbol

    if not force_refresh and is_cache_valid(stock_id):
        df = load_cache(stock_id)
        if df is not None:
            return df

    start = f"{start_year}-01-01"

    if market == "TW":
        print(f"  [Download] Fetching {stock_id} via FinMind...")
        df_new = download_finmind(stock_id, start=start)
    else:
        print(f"  [Download] Fetching {yf_symbol} via yfinance...")
        df_new = download_yf(yf_symbol, start=start)

    df_old = load_cache(stock_id)
    if df_old is not None:
        df = update_cache(stock_id, df_old, df_new)
    else:
        save_cache(stock_id, df_new)
        df = df_new

    return df
