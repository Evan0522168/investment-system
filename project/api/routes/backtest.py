from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from data.data_loader import download_data
from simulator.strategy import STRATEGIES
from simulator.backtest import run_backtest

router = APIRouter()


class BacktestRequest(BaseModel):
    stock_id: str
    strategy_key: str
    initial_cash: float = 1000000
    shares_per_trade: int = 1000


@router.get("/strategies")
def list_strategies():
    return {
        "strategies": [
            {"key": k, "name": v.name}
            for k, v in STRATEGIES.items()
        ]
    }


@router.post("/run")
def run_backtest_api(req: BacktestRequest):
    if req.strategy_key not in STRATEGIES:
        raise HTTPException(status_code=400, detail="Invalid strategy key")
    try:
        df = download_data(req.stock_id)
        strategy = STRATEGIES[req.strategy_key]
        result = run_backtest(df, strategy, req.initial_cash, req.shares_per_trade)

        daily = result["daily_values"][["date", "value", "price"]].copy()
        daily["date"] = daily["date"].astype(str)

        return {
            "strategy": result["strategy"],
            "initial_cash": result["initial_cash"],
            "final_value": round(result["final_value"], 2),
            "total_return": round(result["total_return"], 2),
            "sharpe": round(result["sharpe"], 3),
            "max_drawdown": round(result["max_drawdown"], 2),
            "buy_trades": result["buy_trades"],
            "sell_trades": result["sell_trades"],
            "daily_values": daily.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
