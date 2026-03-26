from fastapi import APIRouter
from data.data_loader import download_data
from api.routes.trade import _account

router = APIRouter()


@router.get("/")
def get_portfolio():
    current_prices = {}
    for stock_id in _account.holdings:
        try:
            df = download_data(stock_id)
            current_prices[stock_id] = df["Close"].iloc[-1]
        except Exception:
            current_prices[stock_id] = _account.holdings[stock_id]["avg_cost"]

    total = _account.portfolio_value(current_prices)
    pnl = total - _account.initial_cash
    pnl_pct = (pnl / _account.initial_cash) * 100

    holdings_detail = []
    for stock_id, info in _account.holdings.items():
        price = current_prices.get(stock_id, info["avg_cost"])
        market_val = info["shares"] * price
        cost_val = info["shares"] * info["avg_cost"]
        stock_pnl = market_val - cost_val
        stock_pnl_pct = (stock_pnl / cost_val) * 100 if cost_val > 0 else 0
        holdings_detail.append({
            "stock_id": stock_id,
            "shares": info["shares"],
            "avg_cost": info["avg_cost"],
            "current_price": round(price, 2),
            "market_value": round(market_val, 2),
            "pnl": round(stock_pnl, 2),
            "pnl_pct": round(stock_pnl_pct, 2)
        })

    return {
        "initial_cash": _account.initial_cash,
        "cash": round(_account.cash, 2),
        "stock_value": round(total - _account.cash, 2),
        "total_value": round(total, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "holdings": holdings_detail
    }
