import pandas as pd


def run_backtest(df, strategy, initial_cash=1000000):
    cash = initial_cash
    holdings = 0
    short_position = 0
    short_entry_price = 0
    daily_values = []
    trade_log = []

    dca_amount = getattr(strategy, 'amount_per_trade', None)

    for i in range(50, len(df)):
        df_slice = df.iloc[:i + 1]
        current_price = df_slice["Close"].iloc[-1]
        current_date = str(df_slice.index[-1].date())

        sig = strategy.signal(df_slice)

        if sig == "BUY" and short_position == 0:
            if dca_amount:
                shares = int(min(dca_amount, cash) // current_price)
            else:
                shares = int(cash // current_price) if holdings == 0 else 0

            if shares > 0:
                cost = shares * current_price
                cash -= cost
                holdings += shares
                trade_log.append({
                    "date": current_date,
                    "action": "BUY",
                    "price": round(current_price, 4),
                    "shares": shares,
                    "amount": round(cost, 2)
                })

        elif sig == "SELL" and holdings > 0:
            revenue = holdings * current_price
            cash += revenue
            trade_log.append({
                "date": current_date,
                "action": "SELL",
                "price": round(current_price, 4),
                "shares": holdings,
                "amount": round(revenue, 2)
            })
            holdings = 0

        elif sig == "SHORT" and short_position == 0 and holdings == 0:
            shares = int(cash * 0.5 // current_price)
            if shares > 0:
                short_position = shares
                short_entry_price = current_price
                trade_log.append({
                    "date": current_date,
                    "action": "SHORT",
                    "price": round(current_price, 4),
                    "shares": shares,
                    "amount": round(shares * current_price, 2)
                })

        elif sig == "COVER" and short_position > 0:
            pnl = (short_entry_price - current_price) * short_position
            cash += pnl
            trade_log.append({
                "date": current_date,
                "action": "COVER",
                "price": round(current_price, 4),
                "shares": short_position,
                "amount": round(abs(pnl), 2)
            })
            short_position = 0
            short_entry_price = 0

        short_pnl = (short_entry_price - current_price) * short_position if short_position > 0 else 0
        total = cash + holdings * current_price + short_pnl
        daily_values.append({
            "date": current_date,
            "value": round(total, 2),
            "price": round(current_price, 4),
        })

    if holdings > 0:
        final_price = df["Close"].iloc[-1]
        cash += holdings * final_price

    if short_position > 0:
        final_price = df["Close"].iloc[-1]
        pnl = (short_entry_price - final_price) * short_position
        cash += pnl

    final_value = round(cash, 2)
    total_return = round((final_value - initial_cash) / initial_cash * 100, 2)

    values_df = pd.DataFrame(daily_values)
    daily_returns = values_df["value"].pct_change().dropna()
    avg_return = daily_returns.mean()
    std_return = daily_returns.std()
    sharpe = round((avg_return / std_return * (252 ** 0.5)), 3) if std_return > 0 else 0

    values_df["peak"] = values_df["value"].cummax()
    values_df["drawdown"] = (values_df["value"] - values_df["peak"]) / values_df["peak"] * 100
    max_drawdown = round(values_df["drawdown"].min(), 2)

    buy_trades = [t for t in trade_log if t["action"] in ["BUY", "SHORT"]]
    sell_trades = [t for t in trade_log if t["action"] in ["SELL", "COVER"]]

    win_trades = 0
    for i in range(min(len(buy_trades), len(sell_trades))):
        if sell_trades[i]["action"] == "SELL" and sell_trades[i]["price"] > buy_trades[i]["price"]:
            win_trades += 1
        elif sell_trades[i]["action"] == "COVER" and sell_trades[i]["price"] < buy_trades[i]["price"]:
            win_trades += 1
    total_closed = min(len(buy_trades), len(sell_trades))
    win_rate = round(win_trades / total_closed * 100, 1) if total_closed > 0 else 0

    return {
        "strategy": strategy.name,
        "initial_cash": initial_cash,
        "final_value": final_value,
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "total_trades": len(trade_log),
        "buy_trades": len(buy_trades),
        "sell_trades": len(sell_trades),
        "trade_log": trade_log,
        "daily_values": values_df[["date", "value", "price"]].to_dict(orient="records")
    }


def compare_strategies(df, strategies, initial_cash=1000000):
    results = []
    for strategy in strategies:
        result = run_backtest(df, strategy, initial_cash)
        results.append(result)
    results.sort(key=lambda x: x["total_return"], reverse=True)
    return results
