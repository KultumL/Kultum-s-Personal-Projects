import os
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

# Gemini optional
_client = None
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

AI_DISABLED_UNTIL = 0
AI_COOLDOWN_SECONDS = 60

CACHE_DURATION = 300           # 5 min
METRIC_CACHE_DURATION = 86400  # 24h
explanation_cache: Dict[str, Dict[str, Any]] = {}

try:
    from google import genai  # type: ignore
    key = os.getenv("GEMINI_API_KEY")
    if key:
        _client = genai.Client(api_key=key)
except Exception:
    _client = None


def ai_ready() -> bool:
    return _client is not None and time.time() >= AI_DISABLED_UNTIL


def fallback_main_explanation(company_name: str, current_price: Any, change_percent: float) -> str:
    try:
        cp = float(current_price) if current_price is not None else None
    except Exception:
        cp = None

    if change_percent >= 10:
        return (
            f"{company_name} jumped {abs(change_percent):.2f}% today. That’s a huge move—usually big news or earnings. "
            "For beginners: exciting, but read why before acting."
        )
    if change_percent <= -10:
        return (
            f"{company_name} fell {abs(change_percent):.2f}% today. That’s a big drop—often bad news or market fear. "
            "For beginners: don’t panic; check what caused it."
        )
    if change_percent > 1:
        return (
            f"{company_name} is up {abs(change_percent):.2f}% today. Stocks move daily from normal trading and news. "
            "For beginners: try to focus on the long-term story."
        )
    if change_percent < -1:
        return (
            f"{company_name} is down {abs(change_percent):.2f}% today. Small drops are common. "
            "For beginners: one day doesn’t define the investment."
        )
    if cp is not None:
        return (
            f"{company_name} is fairly steady around ${cp:.2f} today. "
            "For beginners: steady days often mean no major new information."
        )
    return f"{company_name} is fairly steady today."


def _fallback_pe(pe_ratio: Any) -> str:
    try:
        if pe_ratio is None:
            return "P/E Ratio not available for this stock."
        pe = float(pe_ratio)
        if pe < 15:
            return f"P/E of {pe:.1f} is relatively low (could be cheaper or slower growth)."
        if pe < 25:
            return f"P/E of {pe:.1f} is moderate (common for many stable companies)."
        return f"P/E of {pe:.1f} is high (investors may expect fast growth, but it can be pricey)."
    except Exception:
        return "P/E Ratio not available for this stock."


def _fallback_market_cap(market_cap: Any) -> str:
    try:
        if market_cap is None:
            return "Market cap not available for this stock."
        cap = float(market_cap)
        b = cap / 1_000_000_000
        if b < 2:
            return f"Market cap ~${b:.1f}B: smaller company (often higher risk, sometimes higher growth)."
        if b < 10:
            return f"Market cap ~${b:.1f}B: mid-sized company (balance of risk and growth)."
        if b < 200:
            return f"Market cap ~${b:.1f}B: large company (usually more stable)."
        t = cap / 1_000_000_000_000
        return f"Market cap ~${t:.1f}T: mega-cap (very large, typically more stable)."
    except Exception:
        return "Market cap not available for this stock."


def _fallback_52wk(current_price: Any, hi: Any, lo: Any) -> str:
    try:
        if current_price is None or hi is None or lo is None:
            return "52-week range not available."
        cp = float(current_price)
        hi = float(hi)
        lo = float(lo)
        if hi <= lo:
            return f"52-week range is ${lo:.2f} to ${hi:.2f}."
        pos = ((cp - lo) / (hi - lo)) * 100
        if pos > 80:
            return f"Near the 52-week high (${hi:.2f}). Strong run, but it can pull back."
        if pos < 20:
            return f"Near the 52-week low (${lo:.2f}). Could be a bargain—or a warning."
        return f"In the middle of the 52-week range (${lo:.2f}–${hi:.2f})."
    except Exception:
        return "52-week range not available."


def get_main_explanation(symbol: str, company_name: str, current_price: Any, change_percent: float) -> str:
    global AI_DISABLED_UNTIL

    cache_key = f"main_{symbol}_{round(change_percent, 1)}"
    now = time.time()

    if cache_key in explanation_cache:
        cached = explanation_cache[cache_key]
        if now - cached["timestamp"] < CACHE_DURATION:
            return cached["text"]

    if not ai_ready():
        text = fallback_main_explanation(company_name, current_price, change_percent)
        explanation_cache[cache_key] = {"text": text, "timestamp": now}
        return text

    prompt = f"""
The stock {symbol} ({company_name}) is currently at ${current_price},
with a change of {change_percent:.2f}% from yesterday's close.

Explain this to someone who's never invested before in 2-3 simple sentences.
Be encouraging but honest.
"""

    try:
        resp = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)  # type: ignore
        text = (resp.text or "").strip()
        if not text:
            text = fallback_main_explanation(company_name, current_price, change_percent)
        explanation_cache[cache_key] = {"text": text, "timestamp": now}
        return text
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            AI_DISABLED_UNTIL = time.time() + AI_COOLDOWN_SECONDS
        text = fallback_main_explanation(company_name, current_price, change_percent)
        explanation_cache[cache_key] = {"text": text, "timestamp": now}
        return text


def get_metric_explanations(
    symbol: str,
    company_name: str,
    current_price: Any,
    pe_ratio: Any,
    market_cap: Any,
    week_52_high: Any,
    week_52_low: Any,
) -> Dict[str, str]:
    global AI_DISABLED_UNTIL

    cache_key = f"metrics_{symbol}"
    now = time.time()

    if cache_key in explanation_cache:
        cached = explanation_cache[cache_key]
        if now - cached["timestamp"] < METRIC_CACHE_DURATION:
            return cached["data"]

    fallback = {
        "pe_ratio": _fallback_pe(pe_ratio),
        "market_cap": _fallback_market_cap(market_cap),
        "week_52_range": _fallback_52wk(current_price, week_52_high, week_52_low),
    }

    if not ai_ready():
        explanation_cache[cache_key] = {"data": fallback, "timestamp": now}
        return fallback

    prompt = f"""
Explain these stock metrics for {company_name} ({symbol}) to a complete beginner.
For each metric, write 1-2 sentences in simple language.

Current Price: ${current_price}
P/E Ratio: {pe_ratio if pe_ratio else 'N/A'}
Market Cap: {market_cap if market_cap else 'N/A'}
52 Week High: {week_52_high if week_52_high else 'N/A'}
52 Week Low: {week_52_low if week_52_low else 'N/A'}

Format EXACTLY:
PE_RATIO: ...
MARKET_CAP: ...
WEEK_52_RANGE: ...
"""

    try:
        resp = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)  # type: ignore
        text = (resp.text or "").strip()

        out: Dict[str, str] = {}

        if "PE_RATIO:" in text and "MARKET_CAP:" in text:
            out["pe_ratio"] = text.split("PE_RATIO:")[1].split("MARKET_CAP:")[0].strip()
        else:
            out["pe_ratio"] = fallback["pe_ratio"]

        if "MARKET_CAP:" in text and "WEEK_52_RANGE:" in text:
            out["market_cap"] = text.split("MARKET_CAP:")[1].split("WEEK_52_RANGE:")[0].strip()
        else:
            out["market_cap"] = fallback["market_cap"]

        if "WEEK_52_RANGE:" in text:
            out["week_52_range"] = text.split("WEEK_52_RANGE:")[1].strip()
        else:
            out["week_52_range"] = fallback["week_52_range"]

        explanation_cache[cache_key] = {"data": out, "timestamp": now}
        return out

    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            AI_DISABLED_UNTIL = time.time() + AI_COOLDOWN_SECONDS
        explanation_cache[cache_key] = {"data": fallback, "timestamp": now}
        return fallback

def chat_with_ai(message: str, context: Optional[str] = None) -> str:
    """
    Returns a plain STRING (never a coroutine).
    Uses Gemini if available, otherwise falls back.
    """
    msg = (message or "").strip()
    if not msg:
        return "Ask me anything about stocks—try: “What is P/E?”"

    # If Gemini isn't configured/ready, return a safe fallback
    if not ai_ready():
        if context:
            return f"I can help explain {context.upper()}. Try asking: “What does P/E mean for {context.upper()}?”"
        return "I can help explain stock basics. Try asking: “What is market cap?”"

    # Build prompt
    ctx_line = f"Context stock: {context.upper()}\n" if context else ""
    prompt = (
        "You are a helpful investing tutor for beginners.\n"
        f"{ctx_line}"
        f"User question: {msg}\n\n"
        "Answer in 3-6 short sentences. Be simple and practical."
    )

    try:
        resp = _client.models.generate_content(model=GEMINI_MODEL, contents=prompt)  # type: ignore
        text = (resp.text or "").strip()
        return text or "I couldn’t generate a response right now—try again in a moment."
    except Exception:
        return "I couldn’t reach the AI service right now. Please try again."
