from .symbol_resolver import resolve_market
from .yf_source import download_yf
from .supabase_cache import is_cache_valid, load_cache, save_cache, update_cache


def download_data(symbol, force_refresh=False, start_year=2020):
    # 台股數字代號自動加 .TW
    if symbol.isdigit():
        yf_symbol = f"{symbol}.TW"
    elif symbol.endswith(".TW"):
        yf_symbol = symbol
    else:
        yf_symbol = symbol

    stock_id = symbol.replace(".TW", "")

    if not force_refresh and is_cache_valid(stock_id):
        df = load_cache(stock_id)
        if df is not None:
            return df

    print(f"  [Download] Fetching {yf_symbol} from {start_year} via yfinance...")

    df_new = download_yf(yf_symbol, start=f"{start_year}-01-01")

    df_old = load_cache(stock_id)
    if df_old is not None:
        df = update_cache(stock_id, df_old, df_new)
    else:
        save_cache(stock_id, df_new)
        df = df_new

    return df
