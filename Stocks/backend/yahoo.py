from typing import Any, Dict, List, Optional
import requests


def yahoo_search(query: str, max_results: int = 8) -> List[Dict[str, Any]]:
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "quotesCount": max_results, "newsCount": 0}
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    payload = r.json()

    results: List[Dict[str, Any]] = []
    for item in payload.get("quotes", []):
        sym = item.get("symbol")
        name = item.get("shortname") or item.get("longname") or item.get("name")
        exch = item.get("exchange")
        qtype = item.get("quoteType")

        if sym and qtype in ("EQUITY", "ETF"):
            results.append(
                {
                    "symbol": sym.upper(),
                    "name": name or sym.upper(),
                    "exchange": exch,
                    "type": qtype,
                }
            )

    return results


def resolve_to_ticker(user_input: str) -> Optional[str]:
    q = (user_input or "").strip()
    if not q:
        return None

    try:
        results = yahoo_search(q, max_results=5)
        if results:
            return results[0]["symbol"]
    except Exception:
        return None

    return None
