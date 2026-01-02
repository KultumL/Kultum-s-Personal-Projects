from typing import Any, Dict, List, Set

# Simple in-memory storage (demo-friendly)
user_watchlist: Set[str] = set()
user_alerts: List[Dict[str, Any]] = []


def get_watchlist_symbols() -> List[str]:
    # Demo defaults if empty
    return list(user_watchlist) if user_watchlist else ["AAPL", "TSLA", "MSFT", "GOOGL"]
