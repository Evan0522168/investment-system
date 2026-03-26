import pandas as pd
from datetime import datetime


class Account:

    def __init__(self, initial_cash=1000000.0):
        self.cash = initial_cash
        self.initial_cash = initial_cash
        self.holdings = {}  # { stock_id: { "shares": int, "avg_cost": float } }
        self.trade_history = []  # list of trade dicts

    # ── 買入 ──────────────────────────────────────────────────
    def buy(self, stock_id, shares, price):
        cost = shares * price
        if cost > self.cash:
            print(f"  [買入失敗] 現金不足。需要 {cost:.2f}，目前現金 {self.cash:.2f}")
            return False

        self.cash -= cost

        if stock_id in self.holdings:
            old_shares = self.holdings[stock_id]["shares"]
            old_cost = self.holdings[stock_id]["avg_cost"]
            new_shares = old_shares + shares
            new_avg = (old_shares * old_cost + shares * price) / new_shares
            self.holdings[stock_id]["shares"] = new_shares
            self.holdings[stock_id]["avg_cost"] = round(new_avg, 4)
        else:
            self.holdings[stock_id] = {
                "shares": shares,
                "avg_cost": price
            }

        self._record_trade("BUY", stock_id, shares, price)
        print(f"  [買入] {stock_id}  {shares} 股 @ {price:.2f}  花費 {cost:.2f}  剩餘現金 {self.cash:.2f}")
        return True

    # ── 賣出 ──────────────────────────────────────────────────
    def sell(self, stock_id, shares, price):
        if stock_id not in self.holdings:
            print(f"  [賣出失敗] 未持有 {stock_id}")
            return False

        held = self.holdings[stock_id]["shares"]
        if shares > held:
            print(f"  [賣出失敗] 持股不足。持有 {held} 股，欲賣 {shares} 股")
            return False

        revenue = shares * price
        self.cash += revenue
        self.holdings[stock_id]["shares"] -= shares

        if self.holdings[stock_id]["shares"] == 0:
            del self.holdings[stock_id]

        self._record_trade("SELL", stock_id, shares, price)
        print(f"  [賣出] {stock_id}  {shares} 股 @ {price:.2f}  收入 {revenue:.2f}  剩餘現金 {self.cash:.2f}")
        return True

    # ── 計算總資產 ────────────────────────────────────────────
    def portfolio_value(self, current_prices: dict):
        """
        current_prices: { stock_id: float }
        """
        stock_value = 0.0
        for stock_id, info in self.holdings.items():
            price = current_prices.get(stock_id, info["avg_cost"])
            stock_value += info["shares"] * price
        return round(self.cash + stock_value, 2)

    # ── 損益摘要 ──────────────────────────────────────────────
    def summary(self, current_prices: dict):
        total = self.portfolio_value(current_prices)
        pnl = total - self.initial_cash
        pnl_pct = (pnl / self.initial_cash) * 100

        print("\n" + "=" * 50)
        print("  投資組合摘要")
        print("=" * 50)
        print(f"  起始資金     : {self.initial_cash:,.2f}")
        print(f"  目前現金     : {self.cash:,.2f}")
        print(f"  持股市值     : {total - self.cash:,.2f}")
        print(f"  總資產       : {total:,.2f}")
        print(f"  總損益       : {pnl:+,.2f} ({pnl_pct:+.2f}%)")
        print("-" * 50)

        if self.holdings:
            print("  持股明細：")
            for stock_id, info in self.holdings.items():
                price = current_prices.get(stock_id, info["avg_cost"])
                market_val = info["shares"] * price
                cost_val = info["shares"] * info["avg_cost"]
                stock_pnl = market_val - cost_val
                stock_pnl_pct = (stock_pnl / cost_val) * 100 if cost_val > 0 else 0
                print(f"  {stock_id}  持有 {info['shares']} 股  "
                      f"均價 {info['avg_cost']:.2f}  "
                      f"現價 {price:.2f}  "
                      f"損益 {stock_pnl:+,.2f} ({stock_pnl_pct:+.2f}%)")
        else:
            print("  目前無持股")

        print("=" * 50)

    # ── 交易紀錄 ──────────────────────────────────────────────
    def _record_trade(self, action, stock_id, shares, price):
        self.trade_history.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": action,
            "stock_id": stock_id,
            "shares": shares,
            "price": price,
            "amount": round(shares * price, 2)
        })

    def save_trade_history(self, filename="trade_history.csv"):
        if not self.trade_history:
            print("  尚無交易紀錄")
            return
        df = pd.DataFrame(self.trade_history)
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"  交易紀錄已儲存 → {filename}")