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
            "RSI Strategy",
            f"Buy when RSI < {oversold}, Sell when RSI > {overbought}"
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
            "MACD Strategy",
            "Buy on golden cross, Sell on death cross"
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
            "MA Crossover Strategy",
            f"Buy when SMA{fast} crosses above SMA{slow}, Sell when crosses below"
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
            "Bollinger Band Strategy",
            "Buy when price touches lower band, Sell when price touches upper band"
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
            "RSI + MACD Combined",
            "Buy when RSI oversold AND MACD golden cross, Sell when RSI overbought AND MACD death cross"
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

    def to_dict(self):
        d = super().to_dict()
        return d


class CustomStrategy(Strategy):
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
        
class DCAStrategy(Strategy):
    """
    定期定額 — 每隔固定天數買入固定金額
    不主動賣出，只在回測結束時結算
    """
    def __init__(self, interval_days=30):
        super().__init__(
            "DCA Strategy",
            f"Buy fixed amount every {interval_days} days regardless of price"
        )
        self.interval_days = interval_days
        self._last_buy_idx = None

    def signal(self, df):
        current_idx = len(df) - 1
        if self._last_buy_idx is None:
            self._last_buy_idx = current_idx
            return "BUY"
        if current_idx - self._last_buy_idx >= self.interval_days:
            self._last_buy_idx = current_idx
            return "BUY"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"interval_days": self.interval_days})
        return d


class ShortSellingStrategy(Strategy):
    """
    做空策略 — 當訊號出現時做空（賣出借來的股票）
    使用 RSI 超買時做空，RSI 超賣時回補
    """
    def __init__(self, period=14, overbought=70, oversold=30):
        super().__init__(
            "Short Selling Strategy",
            f"Short when RSI > {overbought}, Cover when RSI < {oversold}"
        )
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def signal(self, df):
        rsi = calc_rsi(df["Close"], self.period)
        latest = rsi.iloc[-1]
        if latest > self.overbought:
            return "SHORT"
        elif latest < self.oversold:
            return "COVER"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"period": self.period, "overbought": self.overbought, "oversold": self.oversold})
        return d


class MeanReversionStrategy(Strategy):
    """
    均值回歸 — 價格偏離均線過多時反向操作
    """
    def __init__(self, period=20, threshold=0.05):
        super().__init__(
            "Mean Reversion Strategy",
            f"Buy when price is {threshold*100}% below SMA{period}, Sell when above"
        )
        self.period = period
        self.threshold = threshold

    def signal(self, df):
        close = df["Close"]
        sma = calc_sma(close, self.period).iloc[-1]
        if sma is None:
            return "HOLD"
        price = close.iloc[-1]
        deviation = (price - sma) / sma
        if deviation < -self.threshold:
            return "BUY"
        elif deviation > self.threshold:
            return "SELL"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"period": self.period, "threshold": self.threshold})
        return d


class BreakoutStrategy(Strategy):
    """
    突破策略 — 價格突破近期高點買入，跌破近期低點賣出
    """
    def __init__(self, lookback=20):
        super().__init__(
            "Breakout Strategy",
            f"Buy on {lookback}-day high breakout, Sell on {lookback}-day low breakdown"
        )
        self.lookback = lookback

    def signal(self, df):
        if len(df) < self.lookback + 1:
            return "HOLD"
        close = df["Close"]
        recent_high = close.iloc[-(self.lookback+1):-1].max()
        recent_low = close.iloc[-(self.lookback+1):-1].min()
        current = close.iloc[-1]
        if current > recent_high:
            return "BUY"
        elif current < recent_low:
            return "SELL"
        return "HOLD"

    def to_dict(self):
        d = super().to_dict()
        d.update({"lookback": self.lookback})
        return d



BUILTIN_STRATEGIES = {
    "rsi": RSIStrategy(),
    "macd": MACDStrategy(),
    "ma": MAStrategy(),
    "bollinger": BollingerStrategy(),
    "combined": CombinedStrategy(),
    "dca": DCAStrategy(),
    "short": ShortSellingStrategy(),
    "mean_reversion": MeanReversionStrategy(),
    "breakout": BreakoutStrategy(),
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
    elif stype == "DCAStrategy":
        return DCAStrategy(
            interval_days=config.get("interval_days", 30)
        )
    elif stype == "ShortSellingStrategy":
        return ShortSellingStrategy(
            period=config.get("period", 14),
            overbought=config.get("overbought", 70),
            oversold=config.get("oversold", 30)
        )
    elif stype == "MeanReversionStrategy":
        return MeanReversionStrategy(
            period=config.get("period", 20),
            threshold=config.get("threshold", 0.05)
        )
    elif stype == "BreakoutStrategy":
        return BreakoutStrategy(
            lookback=config.get("lookback", 20)
        )
    elif stype == "CustomStrategy":
        return CustomStrategy(
            name=config.get("name", "Custom Strategy"),
            description=config.get("description", ""),
            buy_rules=config.get("buy_rules", []),
            sell_rules=config.get("sell_rules", [])
        )
    raise ValueError(f"Unknown strategy type: {stype}")

