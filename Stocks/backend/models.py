from pydantic import BaseModel
from typing import List, Optional


class WatchlistItem(BaseModel):
    symbol: str


class PriceAlert(BaseModel):
    symbol: str
    target_price: float
    direction: str  # "above" or "below"


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None  # ticker user is viewing (optional)


class CompareRequest(BaseModel):
    symbols: List[str]
