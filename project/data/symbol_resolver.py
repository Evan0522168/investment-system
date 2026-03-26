def resolve_market(symbol: str) -> str:
    # 台股通常是數字
    if symbol.isdigit():
        return "TWSE"

    # 台股 yfinance 格式
    if symbol.endswith(".TW"):
        return "TWSE"

    # 其他預設使用 yfinance
    return "YF"


def to_yf_symbol(symbol: str) -> str:
    if symbol.isdigit():
        return f"{symbol}.TW"
    return symbol
