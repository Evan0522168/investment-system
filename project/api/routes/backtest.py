from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from data.data_loader import download_data
from simulator.backtest import run_backtest, compare_strategies
from simulator.strategy import BUILTIN_STRATEGIES, build_strategy, CustomStrategy

router = APIRouter()


class RuleModel(BaseModel):
    indicator: str
    condition: str
    value: Optional[float] = 0
    period: Optional[int] = 14
    fast: Optional[int] = 12
    slow: Optional[int] = 26


class StrategyConfig(BaseModel):
    type: str
    name: Optional[str] = "自訂策略"
    description: Optional[str] = ""
    period: Optional[int] = 14
    oversold: Optional[int] = 30
    overbought: Optional[int] = 70
    fast: Optional[int] = 12
    slow: Optional[int] = 26
    signal: Optional[int] = 9
    num_std: Optional[float] = 2
    buy_rules: Optional[List[RuleModel]] = []
    sell_rules: Optional[List[RuleModel]] = []


class BacktestRequest(BaseModel):
    symbol: str
    market: str = "TWSE"
    strategy: StrategyConfig
    initial_cash: Optional[float] = 1000000
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class CompareRequest(BaseModel):
    symbol: str
    market: str = "TWSE"
    initial_cash: Optional[float] = 1000000


@router.post("/run")
def run_backtest_api(req: BacktestRequest):
    try:
        df = download_data(req.symbol)
        if req.start_date:
            df = df[df.index >= req.start_date]
        if req.end_date:
            df = df[df.index <= req.end_date]
        if len(df) < 60:
            raise HTTPException(status_code=400, detail="Insufficient data for backtest")
        config = req.strategy.dict()
        if config.get("buy_rules"):
            config["buy_rules"] = [r.dict() for r in req.strategy.buy_rules]
        if config.get("sell_rules"):
            config["sell_rules"] = [r.dict() for r in req.strategy.sell_rules]
        strategy = build_strategy(config)
        result = run_backtest(df, strategy, req.initial_cash)
        return result
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"BACKTEST ERROR: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
def compare_backtest_api(req: CompareRequest):
    try:
        df = download_data(req.symbol)
        if len(df) < 60:
            raise HTTPException(status_code=400, detail="資料不足")
        results = compare_strategies(df, list(BUILTIN_STRATEGIES.values()), req.initial_cash)
        return {"symbol": req.symbol, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies")
def get_strategies():
    return {
        "builtin": [s.to_dict() for s in BUILTIN_STRATEGIES.values()],
        "custom_template": {
            "type": "CustomStrategy",
            "name": "我的策略",
            "description": "策略描述",
            "buy_rules": [
                {"indicator": "RSI", "condition": "less_than", "value": 30, "period": 14}
            ],
            "sell_rules": [
                {"indicator": "RSI", "condition": "greater_than", "value": 70, "period": 14}
            ]
        }
    }
"""from fastapi import APIRouter, HTTPException
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
        raise HTTPException(status_code=500, detail=str(
"""