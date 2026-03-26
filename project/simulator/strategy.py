from simulator.indicators import (
    calc_rsi, calc_macd, calc_sma, calc_ema,
    calc_bollinger, calc_stochastic
)


class Strategy:
    """
    每個策略接收 df（價格資料）
    回傳 "BUY"、"SELL" 或 "HOLD"
    """

    def __init__(self, name):
        self.name = name

    def signal(self, df):
        raise NotImplementedError


# ── 策略 1：RSI 超買超賣 ────────────────────────────────────────
class RSIStrategy(Strategy):
    """
    RSI < 30 → BUY
    RSI > 70 → SELL
    其他    → HOLD
    """

    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__("RSI Strategy")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def signal(self, df):
        rsi = calc_rsi(df["Close"], self.period)
        latest = rsi.iloc[-1]
        if latest < self.oversold:
            return "BUY"
        elif latest > self.overbought:
            return "SELL"
        return "HOLD"


# ── 策略 2：MACD 黃金／死亡交叉 ────────────────────────────────
class MACDStrategy(Strategy):
    """
    MACD 線從下穿越 Signal 線 → BUY  （黃金交叉）
    MACD 線從上穿越 Signal 線 → SELL （死亡交叉）
    """

    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__("MACD Strategy")
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def signal(self, df):
        macd_line, signal_line, _ = calc_macd(
            df["Close"], self.fast, self.slow, self.signal_period
        )
        if len(macd_line) < 2:
            return "HOLD"
        prev_macd = macd_line.iloc[-2]
        prev_sig  = signal_line.iloc[-2]
        curr_macd = macd_line.iloc[-1]
        curr_sig  = signal_line.iloc[-1]
        if prev_macd < prev_sig and curr_macd > curr_sig:
            return "BUY"
        elif prev_macd > prev_sig and curr_macd < curr_sig:
            return "SELL"
        return "HOLD"


# ── 策略 3：均線交叉 ────────────────────────────────────────────
class MAStrategy(Strategy):
    """
    SMA20 從下穿越 SMA50 → BUY
    SMA20 從上穿越 SMA50 → SELL
    """

    def __init__(self, fast=20, slow=50):
        super().__init__("MA Crossover Strategy")
        self.fast = fast
        self.slow = slow

    def signal(self, df):
        sma_fast = calc_sma(df["Close"], self.fast)
        sma_slow = calc_sma(df["Close"], self.slow)
        if len(sma_fast) < 2:
            return "HOLD"
        if sma_fast.iloc[-2] < sma_slow.iloc[-2] and sma_fast.iloc[-1] > sma_slow.iloc[-1]:
            return "BUY"
        elif sma_fast.iloc[-2] > sma_slow.iloc[-2] and sma_fast.iloc[-1] < sma_slow.iloc[-1]:
            return "SELL"
        return "HOLD"


# ── 策略 4：布林通道突破 ────────────────────────────────────────
class BollingerStrategy(Strategy):
    """
    收盤價跌破下軌 → BUY
    收盤價突破上軌 → SELL
    """

    def __init__(self, period=20, num_std=2):
        super().__init__("Bollinger Band Strategy")
        self.period = period
        self.num_std = num_std

    def signal(self, df):
        upper, mid, lower = calc_bollinger(df["Close"], self.period, self.num_std)
        close = df["Close"].iloc[-1]
        if close <= lower.iloc[-1]:
            return "BUY"
        elif close >= upper.iloc[-1]:
            return "SELL"
        return "HOLD"


# ── 策略 5：RSI + MACD 組合 ─────────────────────────────────────
class CombinedStrategy(Strategy):
    """
    RSI < 40 且 MACD 黃金交叉 → BUY
    RSI > 60 且 MACD 死亡交叉 → SELL
    """

    def __init__(self):
        super().__init__("Combined RSI + MACD Strategy")
        self.rsi_strategy = RSIStrategy(oversold=40, overbought=60)
        self.macd_strategy = MACDStrategy()

    def signal(self, df):
        rsi_sig  = self.rsi_strategy.signal(df)
        macd_sig = self.macd_strategy.signal(df)
        if rsi_sig == "BUY" and macd_sig == "BUY":
            return "BUY"
        elif rsi_sig == "SELL" and macd_sig == "SELL":
            return "SELL"
        return "HOLD"


# ── 策略清單（供選單使用）──────────────────────────────────────
STRATEGIES = {
    "1": RSIStrategy(),
    "2": MACDStrategy(),
    "3": MAStrategy(),
    "4": BollingerStrategy(),
    "5": CombinedStrategy(),
}


def show_strategy_menu():
    print("\n  選擇策略：")
    print("  [1] RSI 超買超賣")
    print("  [2] MACD 黃金／死亡交叉")
    print("  [3] 均線交叉 (SMA20/50)")
    print("  [4] 布林通道突破")
    print("  [5] RSI + MACD 組合策略")


def select_strategy():
    show_strategy_menu()
    while True:
        choice = input("\n  請選擇策略 (1-5): ").strip()
        if choice in STRATEGIES:
            strategy = STRATEGIES[choice]
            print(f"\n  已選擇：{strategy.name}")
            return strategy
        print("  請輸入 1 到 5")
