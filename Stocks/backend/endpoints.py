from typing import Any, Dict, List
import time

import yfinance as yf
from fastapi import APIRouter, Query

from .models import WatchlistItem, PriceAlert, ChatMessage, CompareRequest
from .store import user_watchlist, user_alerts, get_watchlist_symbols
from .stock_utils import safe_percent_change, looks_like_bad_info, resolve_stock_query
from .yahoo import yahoo_search
from .ai import get_main_explanation, get_metric_explanations, ai_ready, chat_with_ai

from .news import get_company_news

router = APIRouter()


@router.get("/search")
def search_symbols(q: str = Query(..., min_length=1)):
    try:
        return {"query": q, "results": yahoo_search(q, max_results=8)}
    except Exception as e:
        return {"query": q, "results": [], "error": str(e)}


@router.get("/stock/{query}")
def get_stock(query: str):
    symbol, resolved_from, info = resolve_stock_query(query)
    if not symbol or not info:
        return {
            "error": f"Quote not found for: {query}",
            "tip": "Try a ticker like AAPL, TSLA, MSFT, or search by company name using /search?q=...",
        }

    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    previous_close = info.get("previousClose", None)
    company_name = info.get("longName", symbol)

    change_percent = safe_percent_change(current_price, previous_close)
    explanation = get_main_explanation(symbol, company_name, current_price, change_percent)

    return {
        "symbol": symbol,
        "company_name": company_name,
        "price": current_price,
        "change_percent": round(change_percent, 2),
        "explanation": explanation,
        "resolved_from": resolved_from,
    }


@router.post("/watchlist/add")
async def add_to_watchlist(item: WatchlistItem):
    symbol, resolved_from, info = resolve_stock_query(item.symbol)
    if not symbol or not info:
        return {"success": False, "error": f"Quote not found for: {item.symbol}"}

    user_watchlist.add(symbol)
    return {
        "success": True,
        "message": f"Added {symbol} to watchlist",
        "symbol": symbol,
        "company_name": info.get("longName", symbol),
        "watchlist_count": len(user_watchlist),
        "resolved_from": resolved_from,
    }


@router.delete("/watchlist/remove/{query}")
async def remove_from_watchlist(query: str):
    raw = (query or "").strip()
    if not raw:
        return {"success": False, "error": "Symbol is required"}

    symbol = raw.upper()
    if symbol not in user_watchlist:
        sym2, _, _ = resolve_stock_query(raw)
        if sym2:
            symbol = sym2

    if symbol in user_watchlist:
        user_watchlist.remove(symbol)
        global user_alerts
        user_alerts = [a for a in user_alerts if a.get("symbol") != symbol]
        return {
            "success": True,
            "message": f"Removed {symbol} from watchlist",
            "watchlist_count": len(user_watchlist),
        }

    return {"success": False, "error": f"{raw} not in watchlist"}


@router.get("/watchlist/all")
async def get_watchlist():
    symbols = get_watchlist_symbols()
    results: List[Dict[str, Any]] = []

    for sym in symbols:
        try:
            stock = yf.Ticker(sym)
            info = stock.info
            if looks_like_bad_info(info):
                continue

            current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
            previous_close = info.get("previousClose", None)
            change_percent = safe_percent_change(current_price, previous_close)

            stock_alerts = [a for a in user_alerts if a.get("symbol") == sym]

            results.append(
                {
                    "symbol": sym,
                    "company_name": info.get("longName", sym),
                    "price": current_price if current_price is not None else 0,
                    "change_percent": round(change_percent, 2),
                    "has_alert": len(stock_alerts) > 0,
                    "alerts": stock_alerts,
                }
            )
        except Exception:
            continue

    return {"watchlist": results, "total": len(results)}


@router.get("/stock/{query}/details")
async def get_stock_details(query: str):
    symbol, resolved_from, info = resolve_stock_query(query)
    if not symbol or not info:
        return {"error": f"Quote not found for symbol: {query}"}

    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    previous_close = info.get("previousClose", None)
    change_percent = safe_percent_change(current_price, previous_close)
    company_name = info.get("longName", symbol)

    main_explanation = get_main_explanation(symbol, company_name, current_price, change_percent)

    pe_ratio = info.get("trailingPE", None)
    market_cap = info.get("marketCap", None)
    week_52_high = info.get("fiftyTwoWeekHigh", None)
    week_52_low = info.get("fiftyTwoWeekLow", None)

    metric_explanations = get_metric_explanations(
        symbol=symbol,
        company_name=company_name,
        current_price=current_price,
        pe_ratio=pe_ratio,
        market_cap=market_cap,
        week_52_high=week_52_high,
        week_52_low=week_52_low,
    )

    # ✅ NEWS: strongly related ticker-filtered news
    news = get_company_news(symbol, limit=8)

    return {
        "symbol": symbol,
        "company_name": company_name,
        "price": current_price,
        "change_percent": round(change_percent, 2),
        "previous_close": previous_close if previous_close is not None else 0,
        "day_high": info.get("dayHigh", None),
        "day_low": info.get("dayLow", None),
        "week_52_high": week_52_high,
        "week_52_low": week_52_low,
        "pe_ratio": pe_ratio,
        "market_cap": market_cap,
        "volume": info.get("volume", None),
        "main_explanation": main_explanation,
        "metric_explanations": metric_explanations,
        "news": news,
        "resolved_from": resolved_from,
    }


@router.get("/stock/{query}/news")
async def get_stock_news(query: str, limit: int = 8):
    symbol, _, info = resolve_stock_query(query)
    if not symbol or not info:
        return {"error": f"Quote not found for symbol: {query}"}
    return {"symbol": symbol, "news": get_company_news(symbol, limit=limit)}


@router.get("/stock/{query}/history")
async def get_stock_history(query: str, period: str = "1mo"):
    symbol, resolved_from, _ = resolve_stock_query(query)
    if not symbol:
        return {"error": f"Quote not found for: {query}"}

    stock = yf.Ticker(symbol)

    try:
        hist = stock.history(period=period)
        history_data = []
        for date, row in hist.iterrows():
            history_data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }
            )

        return {"symbol": symbol, "period": period, "data": history_data, "resolved_from": resolved_from}
    except Exception as e:
        return {"error": str(e), "symbol": symbol, "period": period}


@router.post("/alerts/add")
async def add_price_alert(alert: PriceAlert):
    raw = (alert.symbol or "").strip()
    if not raw:
        return {"success": False, "error": "Symbol is required"}

    symbol, resolved_from, info = resolve_stock_query(raw)
    if not symbol or not info:
        return {"success": False, "error": f"Quote not found for: {raw}"}

    if alert.direction not in ("above", "below"):
        return {"success": False, "error": "direction must be 'above' or 'below'"}

    alert_data = {
        "symbol": symbol,
        "target_price": float(alert.target_price),
        "direction": alert.direction,
        "created_at": time.time(),
        "resolved_from": resolved_from,
    }

    user_alerts.append(alert_data)
    return {
        "success": True,
        "message": f"Alert set for {symbol} {alert.direction} ${alert.target_price}",
        "alert": alert_data,
    }


@router.get("/alerts/check/{query}")
async def check_alerts(query: str):
    raw = (query or "").strip()
    if not raw:
        return {"error": "Symbol required"}

    symbol, resolved_from, info = resolve_stock_query(raw)
    if not symbol or not info:
        return {"error": f"Quote not found for: {raw}"}

    current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
    if current_price is None:
        return {"error": f"Could not fetch price for {symbol}"}

    triggered = []
    for a in user_alerts:
        if a.get("symbol") != symbol:
            continue
        if a["direction"] == "below" and current_price <= a["target_price"]:
            triggered.append(a)
        if a["direction"] == "above" and current_price >= a["target_price"]:
            triggered.append(a)

    return {
        "symbol": symbol,
        "current_price": current_price,
        "triggered_alerts": triggered,
        "total_alerts": len([a for a in user_alerts if a.get("symbol") == symbol]),
        "resolved_from": resolved_from,
    }


@router.post("/chat")
async def chat_endpoint(chat: ChatMessage):
    if not ai_ready():
        if chat.context:
            return {
                "success": True,
                "response": (
                    f"I can help! You’re asking about {chat.context.upper()}. "
                    "Right now AI responses are limited, but you can still check price, change %, and metrics."
                ),
                "context": chat.context,
            }
        return {
            "success": True,
            "response": (
                "I can help! Try asking “What is a stock?” or “What does P/E mean?” "
                "Open a stock first for more context."
            ),
            "context": None,
        }

    answer = chat_with_ai(chat.message, chat.context)
    return {"success": True, "response": answer, "context": chat.context}


@router.post("/chat/compare")
async def compare_stocks(req: CompareRequest):
    symbols = req.symbols
    if len(symbols) < 2:
        return {"success": False, "error": "Please provide at least 2 stocks to compare"}
    if len(symbols) > 3:
        return {"success": False, "error": "Maximum 3 stocks can be compared at once"}

    stock_data = []
    for s in symbols:
        sym, resolved_from, info = resolve_stock_query(s)
        if not sym or not info:
            continue

        current_price = info.get("currentPrice", info.get("regularMarketPrice", None))
        previous_close = info.get("previousClose", None)
        change_percent = safe_percent_change(current_price, previous_close)

        stock_data.append(
            {
                "symbol": sym,
                "name": info.get("longName", sym),
                "price": current_price,
                "change": round(change_percent, 2),
                "pe_ratio": info.get("trailingPE", None),
                "market_cap": info.get("marketCap", None),
                "resolved_from": resolved_from,
            }
        )

    if len(stock_data) < 2:
        return {"success": False, "error": "Could not fetch data for enough stocks"}

    return {
        "success": True,
        "stocks": stock_data,
        "comparison": "Basic compare is enabled. (You can re-add Gemini compare later.)",
    }
