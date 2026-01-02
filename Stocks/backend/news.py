# backend/news.py
from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
import yfinance as yf


# Alpha Vantage (free key)
ALPHAVANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
ALPHAVANTAGE_BASE = "https://www.alphavantage.co/query"

# Cache news to avoid hitting limits
_NEWS_CACHE: Dict[str, Dict[str, Any]] = {}
NEWS_CACHE_TTL_SECONDS = 10 * 60  # 10 minutes


def _parse_av_time(ts: Optional[str]) -> Optional[str]:
    """
    AlphaVantage returns time like: YYYYMMDDTHHMM
    Example: 20240115T1345
    We'll convert to ISO-ish: YYYY-MM-DD HH:MM
    """
    if not ts:
        return None
    try:
        dt = datetime.strptime(ts, "%Y%m%dT%H%M")
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _fallback_yfinance_news(symbol: str, limit: int) -> List[Dict[str, Any]]:
    """
    yfinance often returns relevant news without any API key.
    This is a nice fallback if AlphaVantage quota is hit.
    """
    out: List[Dict[str, Any]] = []
    try:
        items = yf.Ticker(symbol).news or []
        for it in items[: max(0, limit)]:
            title = it.get("title")
            url = it.get("link")
            source = it.get("publisher") or it.get("provider") or "Unknown"
            published_at = None
            # providerPublishTime is unix seconds
            t = it.get("providerPublishTime")
            if isinstance(t, (int, float)):
                try:
                    published_at = datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    published_at = None

            if title and url:
                out.append(
                    {
                        "title": title,
                        "url": url,
                        "source": source,
                        "published_at": published_at,
                        "summary": None,
                        "relevance": None,
                    }
                )
    except Exception:
        return []

    return out


def get_company_news(
    symbol: str,
    limit: int = 8,
    min_relevance: float = 0.15,
) -> List[Dict[str, Any]]:
    """
    Returns news articles that are strongly related to a ticker.

    How we keep it "actually related":
      1) AlphaVantage filters by tickers={symbol}
      2) We request sort=RELEVANCE
      3) We ALSO filter each article by checking ticker_sentiment includes symbol
         with relevance_score >= min_relevance
    """
    sym = (symbol or "").strip().upper()
    if not sym:
        return []

    # Cache
    now = time.time()
    cache_key = f"{sym}:{limit}:{min_relevance}"
    cached = _NEWS_CACHE.get(cache_key)
    if cached and (now - cached["ts"] < NEWS_CACHE_TTL_SECONDS):
        return cached["data"]

    # If no key, fallback immediately
    if not ALPHAVANTAGE_API_KEY:
        data = _fallback_yfinance_news(sym, limit=limit)
        _NEWS_CACHE[cache_key] = {"ts": now, "data": data}
        return data

    # Pull more than needed, then filter down
    fetch_limit = min(50, max(20, limit * 5))

    params = {
        "function": "NEWS_SENTIMENT",
        "tickers": sym,            # important: only articles that mention the ticker
        "sort": "RELEVANCE",       # important: return most relevant first
        "limit": fetch_limit,
        "apikey": ALPHAVANTAGE_API_KEY,
    }

    try:
        r = requests.get(ALPHAVANTAGE_BASE, params=params, timeout=12)
        r.raise_for_status()
        payload = r.json()

        # AlphaVantage sometimes returns {"Information": "..."} on rate limit
        if not isinstance(payload, dict) or "feed" not in payload:
            data = _fallback_yfinance_news(sym, limit=limit)
            _NEWS_CACHE[cache_key] = {"ts": now, "data": data}
            return data

        feed = payload.get("feed") or []
        results: List[Dict[str, Any]] = []

        for item in feed:
            title = item.get("title")
            url = item.get("url")
            source = item.get("source") or item.get("source_domain") or "Unknown"
            published_at = _parse_av_time(item.get("time_published"))
            summary = item.get("summary")

            # ✅ Hard relevance check: article must explicitly include our ticker in ticker_sentiment
            best_rel = 0.0
            ts_list = item.get("ticker_sentiment") or []
            for ts in ts_list:
                if (ts.get("ticker") or "").upper() == sym:
                    best_rel = max(best_rel, _safe_float(ts.get("relevance_score"), 0.0))

            if best_rel < float(min_relevance):
                continue

            if title and url:
                results.append(
                    {
                        "title": title,
                        "url": url,
                        "source": source,
                        "published_at": published_at,
                        "summary": summary,
                        "relevance": round(best_rel, 3),
                    }
                )

        # Sort by relevance then by published time (best effort)
        def sort_key(a: Dict[str, Any]):
            rel = a.get("relevance") or 0.0
            ts = a.get("published_at") or ""
            return (rel, ts)

        results.sort(key=sort_key, reverse=True)
        results = results[: max(0, limit)]

        # If we filtered too hard and got nothing, relax to fallback
        if not results:
            results = _fallback_yfinance_news(sym, limit=limit)

        _NEWS_CACHE[cache_key] = {"ts": now, "data": results}
        return results

    except Exception:
        data = _fallback_yfinance_news(sym, limit=limit)
        _NEWS_CACHE[cache_key] = {"ts": now, "data": data}
        return data
