import os
import pandas as pd
from datetime import datetime, timedelta


CACHE_DIR = "cache"


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def _cache_path(stock_id):
    return os.path.join(CACHE_DIR, f"{stock_id}.parquet")


def is_cache_valid(stock_id, max_age_hours=12):
    path = _cache_path(stock_id)
    if not os.path.exists(path):
        return False
    modified_time = datetime.fromtimestamp(os.path.getmtime(path))
    age = datetime.now() - modified_time
    return age < timedelta(hours=max_age_hours)


def load_cache(stock_id):
    path = _cache_path(stock_id)
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_parquet(path)
        print(f"  [快取] 從本地讀取 {stock_id}（{len(df)} 筆資料）")
        return df
    except Exception as e:
        print(f"  [快取] 讀取失敗：{e}")
        return None


def save_cache(stock_id, df):
    _ensure_cache_dir()
    path = _cache_path(stock_id)
    try:
        df.to_parquet(path)
        print(f"  [快取] 已儲存 {stock_id} → {path}")
    except Exception as e:
        print(f"  [快取] 儲存失敗：{e}")


def update_cache(stock_id, df_old, df_new):
    combined = pd.concat([df_old, df_new])
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.sort_index(inplace=True)
    save_cache(stock_id, combined)
    print(f"  [快取] 已更新 {stock_id}（合併後共 {len(combined)} 筆）")
    return combined


def clear_cache(stock_id=None):
    if stock_id:
        path = _cache_path(stock_id)
        if os.path.exists(path):
            os.remove(path)
            print(f"  [快取] 已清除 {stock_id}")
        else:
            print(f"  [快取] {stock_id} 無快取資料")
    else:
        if os.path.exists(CACHE_DIR):
            for f in os.listdir(CACHE_DIR):
                os.remove(os.path.join(CACHE_DIR, f))
            print("  [快取] 已清除所有快取")
        else:
            print("  [快取] 無快取資料")


def list_cache():
    if not os.path.exists(CACHE_DIR):
        print("  [快取] 無任何快取資料")
        return
    files = os.listdir(CACHE_DIR)
    if not files:
        print("  [快取] 無任何快取資料")
        return
    print("\n  [快取] 目前快取清單：")
    print(f"  {'股票代碼':<12} {'資料筆數':>10} {'檔案大小':>12} {'最後更新':>22}")
    print("  " + "-" * 58)
    for f in sorted(files):
        path = os.path.join(CACHE_DIR, f)
        stock_id = f.replace(".parquet", "")
        size = os.path.getsize(path)
        modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M")
        try:
            df = pd.read_parquet(path)
            rows = len(df)
        except Exception:
            rows = 0
        print(f"  {stock_id:<12} {rows:>10} {size/1024:>10.1f}KB {modified:>22}")
