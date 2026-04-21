from simulator.indicators import (
    calc_rsi, calc_macd, calc_sma, calc_ema,
    calc_bollinger, calc_stochastic
)


class Strategy:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description

    def signal(self, df):
        raise NotImplementedError

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__
        }


class RSIStrategy(Strategy):
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__(
            "RSI 超買超賣",
            f"RSI < {oversold} 買入，RSI > {overbought} 賣出"
        )
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

    def to_dict(self):
        d = super().to_dict()
        d.update({"period": self.period, "oversold": self.oversold, "overbought": self.overbought})
        return d


class MACDStrategy(Strategy):
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__(
            "MACD 交叉",
            "MACD 黃金交叉買入，死亡交叉賣出"
        )
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def signal(self, df):
        macd_line, signal_line, _ = calc_macd(
            df["Close"], self.fast, self.slow, self.signal_period
        )
        if len(macd_line) < 2:
            return "HOLD"
        if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
            return "BUY"
        elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
            return "SELL"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"fast": self.fast, "slow": self.slow, "signal": self.signal_period})
        return d


class MAStrategy(Strategy):
    def __init__(self, fast=20, slow=50):
        super().__init__(
            "均線交叉",
            f"SMA{fast} 上穿 SMA{slow} 買入，下穿賣出"
        )
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

    def to_dict(self):
        d = super().to_dict()
        d.update({"fast": self.fast, "slow": self.slow})
        return d


class BollingerStrategy(Strategy):
    def __init__(self, period=20, num_std=2):
        super().__init__(
            "布林通道突破",
            "價格跌破下軌買入，突破上軌賣出"
        )
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

    def to_dict(self):
        d = super().to_dict()
        d.update({"period": self.period, "num_std": self.num_std})
        return d


class CombinedStrategy(Strategy):
    def __init__(self):
        super().__init__(
            "RSI + MACD 組合",
            "RSI 超賣且 MACD 黃金交叉買入，RSI 超買且 MACD 死亡交叉賣出"
        )
        self.rsi = RSIStrategy(oversold=40, overbought=60)
        self.macd = MACDStrategy()

    def signal(self, df):
        rsi_sig = self.rsi.signal(df)
        macd_sig = self.macd.signal(df)
        if rsi_sig == "BUY" and macd_sig == "BUY":
            return "BUY"
        elif rsi_sig == "SELL" and macd_sig == "SELL":
            return "SELL"
        return "HOLD"


class CustomStrategy(Strategy):
    """
    使用者自訂策略
    buy_rules 和 sell_rules 是條件列表
    每個條件格式：
    {
        "indicator": "RSI" | "MACD" | "SMA" | "EMA" | "BOLL",
        "condition": "less_than" | "greater_than" | "cross_above" | "cross_below",
        "value": float (用於 less_than / greater_than)
        "period": int (用於 SMA / EMA / RSI)
        "fast": int, "slow": int (用於 MACD / MA crossover)
    }
    """
    def __init__(self, name, description, buy_rules, sell_rules):
        super().__init__(name, description)
        self.buy_rules = buy_rules
        self.sell_rules = sell_rules

    def _evaluate_rule(self, df, rule):
        indicator = rule.get("indicator")
        condition = rule.get("condition")
        value = rule.get("value", 0)
        period = rule.get("period", 14)
        fast = rule.get("fast", 12)
        slow = rule.get("slow", 26)

        close = df["Close"]

        if indicator == "RSI":
            series = calc_rsi(close, period)
            val = series.iloc[-1]
            if condition == "less_than":
                return val < value
            elif condition == "greater_than":
                return val > value

        elif indicator == "SMA":
            series = calc_sma(close, period)
            val = series.iloc[-1]
            if condition == "less_than":
                return close.iloc[-1] < val
            elif condition == "greater_than":
                return close.iloc[-1] > val
            elif condition == "cross_above":
                prev = calc_sma(close, period).iloc[-2]
                return close.iloc[-2] < prev and close.iloc[-1] > val
            elif condition == "cross_below":
                prev = calc_sma(close, period).iloc[-2]
                return close.iloc[-2] > prev and close.iloc[-1] < val

        elif indicator == "EMA":
            series = calc_ema(close, period)
            val = series.iloc[-1]
            if condition == "less_than":
                return close.iloc[-1] < val
            elif condition == "greater_than":
                return close.iloc[-1] > val

        elif indicator == "MACD":
            macd_line, signal_line, _ = calc_macd(close, fast, slow)
            if condition == "cross_above":
                return macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]
            elif condition == "cross_below":
                return macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]
            elif condition == "greater_than":
                return macd_line.iloc[-1] > signal_line.iloc[-1]
            elif condition == "less_than":
                return macd_line.iloc[-1] < signal_line.iloc[-1]

        elif indicator == "BOLL":
            upper, mid, lower = calc_bollinger(close, period)
            if condition == "cross_above":
                return close.iloc[-1] >= upper.iloc[-1]
            elif condition == "cross_below":
                return close.iloc[-1] <= lower.iloc[-1]

        return False

    def signal(self, df):
        if len(df) < 50:
            return "HOLD"
        buy = all(self._evaluate_rule(df, r) for r in self.buy_rules)
        sell = all(self._evaluate_rule(df, r) for r in self.sell_rules)
        if buy:
            return "BUY"
        elif sell:
            return "SELL"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"buy_rules": self.buy_rules, "sell_rules": self.sell_rules})
        return d


BUILTIN_STRATEGIES = {
    "rsi": RSIStrategy(),
    "macd": MACDStrategy(),
    "ma": MAStrategy(),
    "bollinger": BollingerStrategy(),
    "combined": CombinedStrategy(),
}


def build_strategy(config: dict):
    stype = config.get("type")
    if stype == "RSIStrategy":
        return RSIStrategy(
            period=config.get("period", 14),
            oversold=config.get("oversold", 30),
            overbought=config.get("overbought", 70)
        )
    elif stype == "MACDStrategy":
        return MACDStrategy(
            fast=config.get("fast", 12),
            slow=config.get("slow", 26),
            signal=config.get("signal", 9)
        )
    elif stype == "MAStrategy":
        return MAStrategy(
            fast=config.get("fast", 20),
            slow=config.get("slow", 50)
        )
    elif stype == "BollingerStrategy":
        return BollingerStrategy(
            period=config.get("period", 20),
            num_std=config.get("num_std", 2)
        )
    elif stype == "CombinedStrategy":
        return CombinedStrategy()
    elif stype == "CustomStrategy":
        return CustomStrategy(
            name=config.get("name", "自訂策略"),
            description=config.get("description", ""),
            buy_rules=config.get("buy_rules", []),
            sell_rules=config.get("sell_rules", [])
        )
    raise ValueError(f"Unknown strategy type: {stype}")from simulator.indicators import (
    calc_rsi, calc_macd, calc_sma, calc_ema,
    calc_bollinger, calc_stochastic
)

"""
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
"""