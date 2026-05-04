def resolve_market(symbol: str):
    # 全部改走 yfinance，台股加 .TW 後綴
    if symbol.isdigit():
        return "YF_TW"
    if symbol.endswith(".TW"):
        return "YF"
    return "YF"


def to_yf_symbol(symbol: str) -> str:
    if symbol.isdigit():
        return f"{symbol}.TW"
    return symbol
