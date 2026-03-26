import pandas as pd

from data.data_loader import download_data
from data.twse_fundamental import fetch_twse_fundamental
from data.twse_list import get_twse_stock_list
from data.cache import list_cache, clear_cache
from simulator.account import Account
from simulator.charts import generate_charts
from simulator.indicators import (
    calc_sma, calc_ema, calc_rsi, calc_macd,
    calc_bollinger, calc_stochastic, calc_atr, calc_obv
)
from simulator.strategy import select_strategy, STRATEGIES
from simulator.backtest import run_backtest, compare_strategies
from simulator.live import run_live


def main():
    print("=" * 50)
    print("  TWSE Stock Analyzer")
    print("=" * 50)

    print("\nLoading stock list...")
    try:
        stock_list = get_twse_stock_list()
    except Exception as e:
        print(f"  Warning: could not load stock list ({e})")
        stock_list = pd.DataFrame(columns=["Symbol", "Name"])

    print("Loading fundamental data...")
    try:
        all_fundamentals = fetch_twse_fundamental()
    except Exception as e:
        print(f"  Warning: could not load fundamentals ({e})")
        all_fundamentals = pd.DataFrame(columns=["Symbol", "PE", "PB", "DividendYield"])

    acc = Account(initial_cash=1000000)

    while True:
        print("\n" + "=" * 50)
        print("  主選單")
        print("=" * 50)
        print("  [1] 手動模式 — 自己分析、自己下單")
        print("  [2] 自動回測 — 選擇策略，測試歷史表現")
        print("  [3] 自動即時 — 選擇策略，根據今日資料自動執行")
        print("  [4] 快取管理")
        print("  [q] 退出")
        mode = input("\n  請選擇模式 (1/2/3/4/q): ").strip().lower()

        if mode == "q":
            print("\n  --- 最終投資組合 ---")
            acc.summary({})
            acc.save_trade_history("trades.csv")
            print("Exiting.")
            break

        if mode not in ["1", "2", "3", "4"]:
            print("  請輸入 1、2、3、4 或 q")
            continue

        # ── 模式 4：快取管理（不需要輸入股票代碼）────────────
        if mode == "4":
            print("\n  [1] 查看快取清單")
            print("  [2] 清除特定股票快取")
            print("  [3] 清除所有快取")
            cache_choice = input("\n  請選擇 (1/2/3): ").strip()
            if cache_choice == "1":
                list_cache()
            elif cache_choice == "2":
                cid = input("  輸入股票代碼: ").strip()
                clear_cache(cid)
            elif cache_choice == "3":
                confirm = input("  確定清除所有快取？(y/n): ").strip().lower()
                if confirm == "y":
                    clear_cache()
            continue

        # ── 輸入股票代碼（模式 1、2、3 共用）────────────────
        print("\n" + "-" * 50)
        raw = input("  Enter 4-digit TWSE stock code: ").strip()
        if not raw.isdigit() or len(raw) != 4:
            print("  Invalid input. Please enter exactly 4 digits, e.g. 2330")
            continue

        stock_id = raw

        match = stock_list[stock_list["Symbol"] == stock_id]
        company_name = match.iloc[0]["Name"] if not match.empty else ""
        if company_name:
            print(f"\n  Found: {stock_id} - {company_name}")
        else:
            print(f"\n  Stock code: {stock_id} (name not found in list)")

        refresh = input("  是否強制重新下載資料？(y/n，預設 n): ").strip().lower()
        force = refresh == "y"

        print("  Downloading price data...")
        try:
            df = download_data(stock_id, force_refresh=force)
        except Exception as e:
            print(f"  Error downloading price data: {e}")
            continue

        print(f"  {len(df)} trading days loaded ({df.index[0].date()} to {df.index[-1].date()})")

        close = df["Close"]

        # ── 模式 1：手動 ──────────────────────────────────────
        if mode == "1":
            print(f"\n  --- Price Summary ---")
            print(f"  Latest close  : {close.iloc[-1]:.2f} TWD")
            print(f"  Previous close: {close.iloc[-2]:.2f} TWD")
            chg = close.iloc[-1] - close.iloc[-2]
            chg_pct = chg / close.iloc[-2] * 100
            print(f"  Change        : {chg:+.2f} ({chg_pct:+.2f}%)")
            print(f"  52W High      : {close[-252:].max():.2f}")
            print(f"  52W Low       : {close[-252:].min():.2f}")
            print(f"  Avg Volume    : {df['Volume'].mean():,.0f}")

            fund_row = all_fundamentals[all_fundamentals["Symbol"] == stock_id]
            if not fund_row.empty:
                row = fund_row.iloc[0]
                print(f"\n  --- Fundamentals ---")
                print(f"  P/E Ratio      : {row.get('PE', 'N/A')}")
                print(f"  P/B Ratio      : {row.get('PB', 'N/A')}")
                print(f"  Dividend Yield : {row.get('DividendYield', 'N/A')}%")
            else:
                print("\n  Fundamentals: not available for this stock")

            rsi_val = calc_rsi(close).iloc[-1]
            macd_line, signal_line, _ = calc_macd(close)
            sma20 = calc_sma(close, 20).iloc[-1]
            sma50 = calc_sma(close, 50).iloc[-1]

            print(f"\n  --- Indicator Snapshot ---")
            print(f"  RSI(14) : {rsi_val:.2f}  {'[OVERBOUGHT]' if rsi_val > 70 else '[OVERSOLD]' if rsi_val < 30 else '[NEUTRAL]'}")
            print(f"  MACD    : {macd_line.iloc[-1]:.4f}  Signal: {signal_line.iloc[-1]:.4f}  {'[BULLISH]' if macd_line.iloc[-1] > signal_line.iloc[-1] else '[BEARISH]'}")
            print(f"  SMA20   : {sma20:.2f}  SMA50: {sma50:.2f}  {'[UPTREND]' if sma20 > sma50 else '[DOWNTREND]'}")

            chart_choice = input("\n  是否產生技術分析圖表？(y/n): ").strip().lower()
            if chart_choice == "y":
                print("  Generating charts...")
                try:
                    generate_charts(stock_id, df, company_name)
                except Exception as e:
                    print(f"  Chart error: {e}")
            else:
                print("  略過圖表產生。")

            latest_price = close.iloc[-1]
            while True:
                print("\n" + "-" * 50)
                print(f"  股票代碼 : {stock_id}  現價 : {latest_price:.2f} TWD")
                acc.summary({stock_id: latest_price})
                print("\n  [1] 買入")
                print("  [2] 賣出")
                print("  [3] 返回主選單")
                print("  [4] 結束所有操作並退出")
                action = input("\n  請選擇操作 (1/2/3/4): ").strip()

                if action == "1":
                    try:
                        shares = int(input("  輸入買入股數: ").strip())
                        if shares <= 0:
                            print("  股數必須大於 0")
                            continue
                        acc.buy(stock_id, shares, latest_price)
                        acc.save_trade_history("trades.csv")
                    except ValueError:
                        print("  請輸入有效數字")

                elif action == "2":
                    try:
                        shares = int(input("  輸入賣出股數: ").strip())
                        if shares <= 0:
                            print("  股數必須大於 0")
                            continue
                        acc.sell(stock_id, shares, latest_price)
                        acc.save_trade_history("trades.csv")
                    except ValueError:
                        print("  請輸入有效數字")

                elif action == "3":
                    break

                elif action == "4":
                    print("\n  --- 最終投資組合 ---")
                    acc.summary({stock_id: latest_price})
                    acc.save_trade_history("trades.csv")
                    print("Exiting.")
                    return

                else:
                    print("  請輸入 1、2、3 或 4")

        # ── 模式 2：自動回測 ──────────────────────────────────
        elif mode == "2":
            print("\n  是否比較所有策略？")
            print("  [1] 比較所有策略")
            print("  [2] 選擇單一策略回測")
            bt_choice = input("\n  請選擇 (1/2): ").strip()

            if bt_choice == "1":
                compare_strategies(df, list(STRATEGIES.values()))
            else:
                strategy = select_strategy()
                try:
                    shares = int(input("  每次交易股數（預設 1000）: ").strip() or "1000")
                except ValueError:
                    shares = 1000
                run_backtest(df, strategy, shares_per_trade=shares)

        # ── 模式 3：自動即時 ──────────────────────────────────
        elif mode == "3":
            strategy = select_strategy()
            try:
                shares = int(input("  每次交易股數（預設 1000）: ").strip() or "1000")
            except ValueError:
                shares = 1000
            run_live(df, strategy, acc, stock_id, shares_per_trade=shares)


if __name__ == "__main__":
    main()
