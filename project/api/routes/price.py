from fastapi import APIRouter, HTTPException
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
