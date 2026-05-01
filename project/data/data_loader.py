from .symbol_resolver import resolve_market
from .yf_source import download_yf
from .twse_price import download_twse
from .supabase_cache import is_cache_valid, load_cache, save_cache, update_cache


def download_data(symbol, force_refresh=False, start_year=2020):
    market = resolve_market(symbol)
    stock_id = symbol.replace(".TW", "")

    if not force_refresh and is_cache_valid(stock_id):
        df = load_cache(stock_id)
        if df is not None:
            return df

    print(f"  [Download] Fetching {stock_id} from {start_year}...")

    if market == "YF":
        df_new = download_yf(symbol, start=f"{start_year}-01-01")
    elif market == "TWSE":
        df_new = download_twse(stock_id, start_year=start_year)
    else:
        raise ValueError("Unknown market")

    df_old = load_cache(stock_id)
    if df_old is not None:
        df = update_cache(stock_id, df_old, df_new)
    else:
        save_cache(stock_id, df_new)
        df = df_new

    return df
