from simulator.account import Account


def run_live(df, strategy, acc, stock_id, shares_per_trade=1000):
    """
    用最新資料執行策略，判斷今天應該買還是賣
    acc 是從 main.py 傳入的帳戶，跨模式共用
    """
    current_price = df["Close"].iloc[-1]
    current_date = df.index[-1].date()

    print(f"\n  ===== 即時自動交易：{strategy.name} =====")
    print(f"  股票代碼 : {stock_id}")
    print(f"  日期     : {current_date}")
    print(f"  現價     : {current_price:.2f} TWD")

    # 取得策略訊號
    sig = strategy.signal(df)
    print(f"  策略訊號 : {sig}")

    # 執行交易
    if sig == "BUY":
        if stock_id in acc.holdings:
            print(f"  → 已持有 {stock_id}，略過買入")
        else:
            confirm = input(f"\n  策略建議買入 {shares_per_trade} 股 @ {current_price:.2f}，確認執行？(y/n): ").strip().lower()
            if confirm == "y":
                acc.buy(stock_id, shares_per_trade, current_price)
                acc.save_trade_history("trades.csv")
            else:
                print("  → 已取消")

    elif sig == "SELL":
        if stock_id not in acc.holdings:
            print(f"  → 未持有 {stock_id}，略過賣出")
        else:
            held = acc.holdings[stock_id]["shares"]
            confirm = input(f"\n  策略建議賣出 {held} 股 @ {current_price:.2f}，確認執行？(y/n): ").strip().lower()
            if confirm == "y":
                acc.sell(stock_id, held, current_price)
                acc.save_trade_history("trades.csv")
            else:
                print("  → 已取消")

    else:
        print(f"  → 訊號為 HOLD，今日不操作")

    # 顯示目前帳戶狀態
    acc.summary({stock_id: current_price})
