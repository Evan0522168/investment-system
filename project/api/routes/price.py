from fastapi import APIRouter, HTTPException
from data.data_loader import download_data
from data.supabase_cache import clear_cache
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter()


@router.get("/debug/twse-test")
def debug_twse():
    try:
        url = "https://www.twse.com.tw/exchangeReport/STOCK_DAY"
        params = {"response": "json", "date": "20230101", "stockNo": "0050"}
        r = requests.get(url, params=params, timeout=10, verify=False)
        return {
            "status_code": r.status_code,
            "content_type": r.headers.get("Content-Type"),
            "body_preview": r.text[:500]
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/{symbol}")
def get_price(symbol: str):
    try:
        df = download_data(symbol)
        close = df["Close"]
        return {
            "symbol": symbol,
            "latest_close": round(close.iloc[-1], 4),
            "previous_close": round(close.iloc[-2], 4),
            "change": round(close.iloc[-1] - close.iloc[-2], 4),
            "change_pct": round((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100, 2),
            "high_52w": round(close[-252:].max(), 4),
            "low_52w": round(close[-252:].min(), 4),
            "total_days": len(df),
            "date_range": {
                "start": str(df.index[0].date()),
                "end": str(df.index[-1].date())
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{symbol}/update")
def update_price(symbol: str, start_year: int = 2020):
    try:
        clear_cache(symbol)
        df = download_data(symbol, force_refresh=True, start_year=start_year)
        return {
            "success": True,
            "symbol": symbol,
            "total_days": len(df),
            "latest_date": str(df.index[-1].date()),
            "earliest_date": str(df.index[0].date())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history")
def get_history(symbol: str, days: int = 365):
    try:
        df = download_data(symbol)
        df_slice = df.tail(days)
        records = []
        for date, row in df_slice.iterrows():
            records.append({
                "date": str(date.date()),
                "open": round(row["Open"], 4),
                "high": round(row["High"], 4),
                "low": round(row["Low"], 4),
                "close": round(row["Close"], 4),
                "volume": int(row["Volume"])
            })
        return {"symbol": symbol, "days": days, "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
