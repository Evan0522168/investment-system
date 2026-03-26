import pandas as pd
from simulator.account import Account


def run_backtest(df, strategy, initial_cash=1000000, shares_per_trade=1000):
    """
    逐日跑歷史資料，套用策略自動買賣
    回傳結果摘要
    """
    acc = Account(initial_cash=initial_cash)
    daily_values = []
    trade_log = []

    print(f"\n  開始回測：{strategy.name}")
    print(f"  資料範圍：{df.index[0].date()} → {df.index[-1].date()}")
    print(f"  總交易日：{len(df)} 天")
    print(f"  起始資金：{initial_cash:,.0f}")
    print("-" * 50)

    for i in range(50, len(df)):
        # 取到第 i 天為止的資料
        df_slice = df.iloc[:i + 1]
        current_price = df_slice["Close"].iloc[-1]
        current_date = df_slice.index[-1].date()

        # 取得策略訊號
        sig = strategy.signal(df_slice)

        # 執行交易
        if sig == "BUY":
            # 只在未持有時買入
            stock_id = "STOCK"
            if stock_id not in acc.holdings:
                acc.buy(stock_id, shares_per_trade, current_price)
                trade_log.append({
                    "date": current_date,
                    "action": "BUY",
                    "price": current_price,
                    "shares": shares_per_trade
                })

        elif sig == "SELL":
            stock_id = "STOCK"
            if stock_id in acc.holdings:
                held = acc.holdings[stock_id]["shares"]
                acc.sell(stock_id, held, current_price)
                trade_log.append({
                    "date": current_date,
                    "action": "SELL",
                    "price": current_price,
                    "shares": held
                })

        # 記錄每日資產價值
        portfolio_val = acc.portfolio_value({"STOCK": current_price})
        daily_values.append({
            "date": current_date,
            "value": portfolio_val,
            "price": current_price
        })

    # 結算
    final_price = df["Close"].iloc[-1]
    stock_id = "STOCK"
    if stock_id in acc.holdings:
        held = acc.holdings[stock_id]["shares"]
        acc.sell(stock_id, held, final_price)

    final_value = acc.portfolio_value({})
    total_return = ((final_value - initial_cash) / initial_cash) * 100

    # 計算 Sharpe Ratio
    values_df = pd.DataFrame(daily_values)
    values_df["daily_return"] = values_df["value"].pct_change()
    avg_return = values_df["daily_return"].mean()
    std_return = values_df["daily_return"].std()
    sharpe = (avg_return / std_return * (252 ** 0.5)) if std_return > 0 else 0

    # 計算最大回撤
    values_df["peak"] = values_df["value"].cummax()
    values_df["drawdown"] = (values_df["value"] - values_df["peak"]) / values_df["peak"] * 100
    max_drawdown = values_df["drawdown"].min()

    # 統計
    buy_trades  = [t for t in trade_log if t["action"] == "BUY"]
    sell_trades = [t for t in trade_log if t["action"] == "SELL"]

    print(f"\n  ===== 回測結果：{strategy.name} =====")
    print(f"  起始資金     : {initial_cash:>15,.0f}")
    print(f"  最終資產     : {final_value:>15,.2f}")
    print(f"  總報酬率     : {total_return:>14.2f}%")
    print(f"  Sharpe Ratio : {sharpe:>15.3f}")
    print(f"  最大回撤     : {max_drawdown:>14.2f}%")
    print(f"  買入次數     : {len(buy_trades):>15}")
    print(f"  賣出次數     : {len(sell_trades):>15}")
    print(f"  總交易次數   : {len(trade_log):>15}")
    print("=" * 50)

    # 儲存交易紀錄
    if trade_log:
        trade_df = pd.DataFrame(trade_log)
        filename = f"backtest_{strategy.name.replace(' ', '_')}.csv"
        trade_df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"  交易紀錄已儲存 → {filename}")

    return {
        "strategy": strategy.name,
        "initial_cash": initial_cash,
        "final_value": final_value,
        "total_return": total_return,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "buy_trades": len(buy_trades),
        "sell_trades": len(sell_trades),
        "daily_values": values_df
    }


def compare_strategies(df, strategies, initial_cash=1000000, shares_per_trade=1000):
    """
    同時回測多個策略並比較結果
    """
    results = []
    for strategy in strategies:
        result = run_backtest(df, strategy, initial_cash, shares_per_trade)
        results.append(result)

    print("\n  ===== 策略比較 =====")
    print(f"  {'策略':<30} {'總報酬':>10} {'Sharpe':>10} {'最大回撤':>10} {'交易次數':>10}")
    print("-" * 75)
    for r in results:
        print(f"  {r['strategy']:<30} "
              f"{r['total_return']:>9.2f}% "
              f"{r['sharpe']:>10.3f} "
              f"{r['max_drawdown']:>9.2f}% "
              f"{r['buy_trades'] + r['sell_trades']:>10}")
    print("=" * 75)

    best = max(results, key=lambda x: x["total_return"])
    print(f"\n  最佳策略：{best['strategy']}  報酬率：{best['total_return']:.2f}%")

    return results
