from fastapi import APIRouter, HTTPException
from data.data_loader import download_data
from data.cache import clear_cache

router = APIRouter()


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
def update_price(symbol: str):
    try:
        clear_cache(symbol)
        df = download_data(symbol, force_refresh=True)
        return {
            "success": True,
            "symbol": symbol,
            "total_days": len(df),
            "latest_date": str(df.index[-1].date())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/history")
def get_history(symbol: str, days: int = 90):
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
"""from fastapi import APIRouter, HTTPException
from data.data_loader import download_data

router = APIRouter()


@router.get("/{stock_id}")
def get_price(stock_id: str, force_refresh: bool = False):
    if not stock_id.isdigit() or len(stock_id) != 4:
        raise HTTPException(status_code=400, detail="Invalid stock code. Must be 4 digits.")
    try:
        df = download_data(stock_id, force_refresh=force_refresh)
        close = df["Close"]
        latest = close.iloc[-1]
        prev = close.iloc[-2]
        change = round(latest - prev, 2)
        change_pct = round((change / prev) * 100, 2)
        return {
            "stock_id": stock_id,
            "latest_close": latest,
            "previous_close": prev,
            "change": change,
            "change_pct": change_pct,
            "high_52w": round(close[-252:].max(), 2),
            "low_52w": round(close[-252:].min(), 2),
            "avg_volume": round(df["Volume"].mean(), 0),
            "date_range": {
                "start": str(df.index[0].date()),
                "end": str(df.index[-1].date())
            },
            "total_days": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{stock_id}/history")
def get_history(stock_id: str, days: int = 90):
    if not stock_id.isdigit() or len(stock_id) != 4:
        raise HTTPException(status_code=400, detail="Invalid stock code.")
    try:
        df = download_data(stock_id)
        df_slice = df.tail(days)
        records = []
        for date, row in df_slice.iterrows():
            records.append({
                "date": str(date.date()),
                "open": round(row["Open"], 2),
                "high": round(row["High"], 2),
                "low": round(row["Low"], 2),
                "close": round(row["Close"], 2),
                "volume": int(row["Volume"])
            })
        return {
            "stock_id": stock_id,
            "days": days,
            "data": records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""