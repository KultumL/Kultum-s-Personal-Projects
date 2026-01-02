from typing import Any, Dict, Optional, Tuple
import yfinance as yf

from .yahoo import resolve_to_ticker


def safe_percent_change(current_price: Any, previous_close: Any) -> float:
    try:
        if current_price is None or previous_close is None:
            return 0.0
        current_price = float(current_price)
        previous_close = float(previous_close)
        if previous_close == 0:
            return 0.0
        return ((current_price - previous_close) / previous_close) * 100.0
    except Exception:
        return 0.0


def looks_like_bad_info(info: Dict[str, Any]) -> bool:
    if not info:
        return True
    if (
        info.get("quoteType") is None
        and info.get("currentPrice") is None
        and info.get("regularMarketPrice") is None
    ):
        return True
    return False


def resolve_stock_query(raw: str) -> Tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
    """
    Returns: (symbol, resolved_from, info)
    - symbol: the final ticker
    - resolved_from: original input if it had to be resolved, else None
    - info: yfinance info dict if found
    """
    original = (raw or "").strip()
    if not original:
        return None, None, None

    symbol = original.upper()

    # 1) Try as ticker
    stock = yf.Ticker(symbol)
    info = stock.info
    if not looks_like_bad_info(info):
        return symbol, None, info

    # 2) Try resolving from company name / wrong symbol
    resolved = resolve_to_ticker(original)
    if not resolved:
        return None, None, None

    stock = yf.Ticker(resolved)
    info = stock.info
    if looks_like_bad_info(info):
        return None, None, None

    return resolved, original.upper(), info
