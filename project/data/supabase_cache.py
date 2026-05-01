import pandas as pd
from datetime import datetime, timedelta
from supabase import create_client

SUPABASE_URL = "https://xdqyxikxdhetccqmstyr.supabase.co"
SUPABASE_KEY = "sb_publishable_G0WQRYPJnGLsmnWYSN60tw_rdm4YRjr"

client = create_client(SUPABASE_URL, SUPABASE_KEY)


def is_cache_valid(symbol, max_age_hours=12):
    try:
        result = client.table("stock_cache") \
            .select("updated_at") \
            .eq("symbol", symbol) \
            .order("updated_at", desc=True) \
            .limit(1) \
            .execute()
        if not result.data:
            return False
        updated_at = datetime.fromisoformat(
            result.data[0]["updated_at"].replace("Z", "+00:00")
        )
        age = datetime.now(updated_at.tzinfo) - updated_at
        return age < timedelta(hours=max_age_hours)
    except Exception as e:
        print(f"  [Supabase] Cache check failed: {e}")
        return False


def load_cache(symbol):
    try:
        result = client.table("stock_cache") \
            .select("*") \
            .eq("symbol", symbol) \
            .order("date") \
            .execute()
        if not result.data:
            return None
        df = pd.DataFrame(result.data)
        df["Date"] = pd.to_datetime(df["date"])
        df.set_index("Date", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]]
        df.columns = ["Open", "High", "Low", "Close", "Volume"]
        print(f"  [Supabase] Loaded {symbol} ({len(df)} rows)")
        return df
    except Exception as e:
        print(f"  [Supabase] Load failed: {e}")
        return None


def save_cache(symbol, df):
    try:
        rows = []
        for date, row in df.iterrows():
            rows.append({
                "symbol": symbol,
                "date": str(date.date()),
                "open": float(row["Open"]) if pd.notna(row["Open"]) else None,
                "high": float(row["High"]) if pd.notna(row["High"]) else None,
                "low": float(row["Low"]) if pd.notna(row["Low"]) else None,
                "close": float(row["Close"]) if pd.notna(row["Close"]) else None,
                "volume": float(row["Volume"]) if pd.notna(row["Volume"]) else None,
                "updated_at": datetime.now().isoformat(),
            })

        batch_size = 500
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            client.table("stock_cache") \
                .upsert(batch, on_conflict="symbol,date") \
                .execute()

        print(f"  [Supabase] Saved {symbol} ({len(rows)} rows)")
    except Exception as e:
        print(f"  [Supabase] Save failed: {e}")


def update_cache(symbol, df_old, df_new):
    combined = pd.concat([df_old, df_new])
    combined = combined[~combined.index.duplicated(keep="last")]
    combined.sort_index(inplace=True)
    save_cache(symbol, combined)
    print(f"  [Supabase] Updated {symbol} ({len(combined)} rows)")
    return combined


def clear_cache(symbol=None):
    try:
        if symbol:
            client.table("stock_cache").delete().eq("symbol", symbol).execute()
            print(f"  [Supabase] Cleared {symbol}")
        else:
            client.table("stock_cache").delete().neq("symbol", "").execute()
            print("  [Supabase] Cleared all cache")
    except Exception as e:
        print(f"  [Supabase] Clear failed: {e}")
