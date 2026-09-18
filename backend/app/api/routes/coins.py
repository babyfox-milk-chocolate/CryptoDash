from fastapi import APIRouter, Depends, HTTPException, Query
import httpx

from app.api.deps import get_current_user
from app.db.models import User
from app.services.coingecko import get_coins_market_data, get_coin_full
from app.schemas.coins import CoinFull, CoinMarket

router = APIRouter(prefix='/coins', tags=['coins'])


@router.get('', response_model=list[CoinMarket])
async def list_coins(
    ids: str = Query(..., description='Монеты через запятую'),
    current_user: User = Depends(get_current_user),
):
    coin_ids = [c.strip() for c in ids.split(",") if c.strip()]
    try: 
        return await get_coins_market_data(coin_ids)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"CoinGecko error: {e.response.status_code}")

# response_model - фильтруем возвращаемые поля, оставляем только нужные  
@router.get('/{coin_id}', response_model=CoinFull)
async def coin_detail(
    coin_id: str, 
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_user),
):
    try:
        return await get_coin_full(coin_id, days)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"CoinGecko error {e.reponse.status_code}")