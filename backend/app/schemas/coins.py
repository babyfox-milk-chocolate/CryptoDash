from pydantic import BaseModel


class CoinMarket(BaseModel):
    id: str
    symbol: str
    name: str
    image: str | None = None
    current_price: float | None = None
    price_change_percentage_24h: float | None = None
    market_cap: float | None = None

class CoinFull(BaseModel):
    market: CoinMarket | None
    history: dict 