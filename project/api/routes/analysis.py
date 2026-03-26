from fastapi import APIRouter, HTTPException
from data.data_loader import download_data
from simulator.indicators import (
    calc_rsi, calc_macd, calc_sma, calc_ema,
    calc_bollinger, calc_stochastic, calc_atr, calc_obv
)

router = APIRouter()


@router.get("/{stock_id}")
def get_analysis(stock_id: str):
    if not stock_id.isdigit() or len(stock_id) != 4:
        raise HTTPException(status_code=400, detail="Invalid stock code.")
    try:
        df = download_data(stock_id)
        close = df["Close"]

        rsi = calc_rsi(close).iloc[-1]
        macd_line, signal_line, histogram = calc_macd(close)
        sma20 = calc_sma(close, 20).iloc[-1]
        sma50 = calc_sma(close, 50).iloc[-1]
        sma200 = calc_sma(close, 200).iloc[-1]
        bb_upper, bb_mid, bb_lower = calc_bollinger(close)
        stoch_k, stoch_d = calc_stochastic(df)
        atr = calc_atr(df).iloc[-1]
        obv = calc_obv(df).iloc[-1]

        return {
            "stock_id": stock_id,
            "rsi": round(rsi, 2),
            "rsi_signal": "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NEUTRAL",
            "macd": {
                "macd_line": round(macd_line.iloc[-1], 4),
                "signal_line": round(signal_line.iloc[-1], 4),
                "histogram": round(histogram.iloc[-1], 4),
                "signal": "BULLISH" if macd_line.iloc[-1] > signal_line.iloc[-1] else "BEARISH"
            },
            "moving_averages": {
                "sma20": round(sma20, 2),
                "sma50": round(sma50, 2),
                "sma200": round(sma200, 2) if sma200 else None,
                "trend": "UPTREND" if sma20 > sma50 else "DOWNTREND"
            },
            "bollinger": {
                "upper": round(bb_upper.iloc[-1], 2),
                "middle": round(bb_mid.iloc[-1], 2),
                "lower": round(bb_lower.iloc[-1], 2)
            },
            "stochastic": {
                "k": round(stoch_k.iloc[-1], 2),
                "d": round(stoch_d.iloc[-1], 2)
            },
            "atr": round(atr, 2),
            "obv": int(obv)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
