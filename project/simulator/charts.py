import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from simulator.indicators import (
    calc_sma, calc_ema, calc_rsi, calc_macd,
    calc_bollinger, calc_stochastic, calc_atr, calc_obv
)


def generate_charts(stock_id, df, company_name=""):
    close = df["Close"]
    sma20 = calc_sma(close, 20)
    sma50 = calc_sma(close, 50)
    sma200 = calc_sma(close, 200)
    rsi = calc_rsi(close)
    macd_line, signal_line, histogram = calc_macd(close)
    bb_upper, bb_mid, bb_lower = calc_bollinger(close)
    stoch_k, stoch_d = calc_stochastic(df)
    atr = calc_atr(df)
    obv = calc_obv(df)
    title = f"{stock_id}  {company_name}"
    fig = plt.figure(figsize=(16, 20), facecolor="#0d1117")
    fig.suptitle(title, color="#e8edf2", fontsize=14, fontweight="bold", y=0.98)
    gs = gridspec.GridSpec(6, 1, figure=fig, height_ratios=[4, 1, 1.5, 1.5, 1.5, 1.5], hspace=0.08)
    ax_price = fig.add_subplot(gs[0])
    ax_vol   = fig.add_subplot(gs[1], sharex=ax_price)
    ax_rsi   = fig.add_subplot(gs[2], sharex=ax_price)
    ax_macd  = fig.add_subplot(gs[3], sharex=ax_price)
    ax_stoch = fig.add_subplot(gs[4], sharex=ax_price)
    ax_obv   = fig.add_subplot(gs[5], sharex=ax_price)
    panel_color = "#161b22"
    for ax in [ax_price, ax_vol, ax_rsi, ax_macd, ax_stoch, ax_obv]:
        ax.set_facecolor(panel_color)
        ax.tick_params(colors="#888", labelsize=7)
        ax.yaxis.label.set_color("#888")
        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")
    ax_price.plot(close.index, close, color="#58a6ff", linewidth=1.2, label="Close")
    ax_price.plot(sma20.index, sma20, color="#ffd700", linewidth=0.9, linestyle="--", label="SMA20")
    ax_price.plot(sma50.index, sma50, color="#ff6b9d", linewidth=0.9, linestyle="--", label="SMA50")
    ax_price.plot(sma200.index, sma200, color="#a371f7", linewidth=0.9, linestyle="--", label="SMA200")
    ax_price.fill_between(close.index, bb_upper, bb_lower, alpha=0.08, color="#58a6ff", label="Bollinger")
    ax_price.plot(bb_upper.index, bb_upper, color="#58a6ff", linewidth=0.5, linestyle=":")
    ax_price.plot(bb_lower.index, bb_lower, color="#58a6ff", linewidth=0.5, linestyle=":")
    ax_price.legend(loc="upper left", fontsize=7, facecolor="#161b22", labelcolor="#ccc", framealpha=0.7)
    ax_price.set_ylabel("Price (TWD)", fontsize=8)
    ax_price.grid(True, color="#21262d", linewidth=0.5)
    plt.setp(ax_price.get_xticklabels(), visible=False)
    colors = ["#3fb950" if c >= o else "#f85149" for c, o in zip(df["Close"], df["Open"])]
    ax_vol.bar(df.index, df["Volume"], color=colors, width=1, alpha=0.8)
    ax_vol.set_ylabel("Volume", fontsize=8)
    ax_vol.grid(True, color="#21262d", linewidth=0.5)
    plt.setp(ax_vol.get_xticklabels(), visible=False)
    ax_rsi.plot(rsi.index, rsi, color="#ffd700", linewidth=1)
    ax_rsi.axhline(70, color="#f85149", linewidth=0.7, linestyle="--")
    ax_rsi.axhline(30, color="#3fb950", linewidth=0.7, linestyle="--")
    ax_rsi.axhline(50, color="#555", linewidth=0.5, linestyle=":")
    ax_rsi.fill_between(rsi.index, rsi, 70, where=(rsi >= 70), alpha=0.15, color="#f85149")
    ax_rsi.fill_between(rsi.index, rsi, 30, where=(rsi <= 30), alpha=0.15, color="#3fb950")
    ax_rsi.set_ylim(0, 100)
    ax_rsi.set_ylabel("RSI(14)", fontsize=8)
    ax_rsi.grid(True, color="#21262d", linewidth=0.5)
    plt.setp(ax_rsi.get_xticklabels(), visible=False)
    ax_macd.plot(macd_line.index, macd_line, color="#58a6ff", linewidth=1, label="MACD")
    ax_macd.plot(signal_line.index, signal_line, color="#ff6b9d", linewidth=1, label="Signal")
    hist_colors = ["#3fb950" if v >= 0 else "#f85149" for v in histogram]
    ax_macd.bar(histogram.index, histogram, color=hist_colors, width=1, alpha=0.6, label="Histogram")
    ax_macd.axhline(0, color="#555", linewidth=0.5)
    ax_macd.legend(loc="upper left", fontsize=7, facecolor="#161b22", labelcolor="#ccc", framealpha=0.7)
    ax_macd.set_ylabel("MACD", fontsize=8)
    ax_macd.grid(True, color="#21262d", linewidth=0.5)
    plt.setp(ax_macd.get_xticklabels(), visible=False)
    ax_stoch.plot(stoch_k.index, stoch_k, color="#ffd700", linewidth=1, label="%K")
    ax_stoch.plot(stoch_d.index, stoch_d, color="#a371f7", linewidth=1, label="%D")
    ax_stoch.axhline(80, color="#f85149", linewidth=0.7, linestyle="--")
    ax_stoch.axhline(20, color="#3fb950", linewidth=0.7, linestyle="--")
    ax_stoch.set_ylim(0, 100)
    ax_stoch.legend(loc="upper left", fontsize=7, facecolor="#161b22", labelcolor="#ccc", framealpha=0.7)
    ax_stoch.set_ylabel("Stoch", fontsize=8)
    ax_stoch.grid(True, color="#21262d", linewidth=0.5)
    plt.setp(ax_stoch.get_xticklabels(), visible=False)
    ax_obv.plot(obv.index, obv, color="#3fb950", linewidth=1)
    ax_obv.set_ylabel("OBV", fontsize=8)
    ax_obv.grid(True, color="#21262d", linewidth=0.5)
    ax_obv.tick_params(axis="x", labelsize=7, rotation=30)
    filename = f"{stock_id}_analysis.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    plt.close()
    print(f"\n  Chart saved -> {filename}")
