"""from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from simulator.account import Account
from api.database import (
    init_db, save_trade, save_account,
    save_holdings, load_account, load_holdings, load_trades
)

router = APIRouter()

# 初始化資料庫
init_db()

# 從資料庫載入帳戶狀態
def _load_account():
    acc = Account(initial_cash=1000000)
    saved = load_account()
    if saved:
        acc.cash = saved["cash"]
        acc.initial_cash = saved["initial_cash"]
    acc.holdings = load_holdings()
    acc.trade_history = load_trades()
    return acc

_account = _load_account()


class TradeRequest(BaseModel):
    stock_id: str
    shares: int
    price: float
    action: str


@router.post("/execute")
def execute_trade(req: TradeRequest):
    if req.action not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Action must be 'buy' or 'sell'")
    if req.shares <= 0:
        raise HTTPException(status_code=400, detail="Shares must be greater than 0")
    if req.price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")

    if req.action == "buy":
        success = _account.buy(req.stock_id, req.shares, req.price)
    else:
        success = _account.sell(req.stock_id, req.shares, req.price)

    if not success:
        raise HTTPException(status_code=400, detail="Trade failed. Check cash or holdings.")

    # 儲存到資料庫
    save_trade(req.action, req.stock_id, req.shares, req.price)
    save_account(_account.cash, _account.initial_cash)
    save_holdings(_account.holdings)

    return {
        "success": True,
        "action": req.action,
        "stock_id": req.stock_id,
        "shares": req.shares,
        "price": req.price,
        "amount": round(req.shares * req.price, 2),
        "cash_remaining": round(_account.cash, 2)
    }


@router.get("/history")
def get_trade_history():
    trades = load_trades()
    return {
        "total_trades": len(trades),
        "trades": trades
    }


@router.delete("/reset")
def reset_account():
    global _account
    import sqlite3
    from api.database import DB_PATH
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM trades")
    conn.execute("DELETE FROM account")
    conn.execute("DELETE FROM holdings")
    conn.commit()
    conn.close()
    _account = Account(initial_cash=1000000)
    return {"success": True, "message": "帳戶已重置"}
"""