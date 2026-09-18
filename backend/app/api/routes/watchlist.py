from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, get_current_user
from app.db.models import User, WatchlistItem
from app.services.coingecko import get_coins_market_data
from app.schemas.watchlist import WathlistAdd, WatchlistItemOut
from app.schemas.coins import CoinMarket


router = APIRouter(prefix='/watchlist', tags=['wathlist'])


@router.get('', response_model=list[WatchlistItemOut])
async def list_watchlist(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.scalars(
        select(WatchlistItem).where(WatchlistItem.user_id == current_user.id)
    )

    return result.all()


@router.post('', response_model=WatchlistItemOut, status_code=201)
async def add_to_watchlist(
    data: WathlistAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = WatchlistItem(user_id=current_user.id, coin_id=data.coin_id)
    db.add(item)
    try:
        await db.commit()
        await db.refresh(item)
    except IntegrityError: # сработал UniqueConstraint(user_id, coin_id) — монета уже в списке
        await db.rollback()
        raise HTTPException(status_code=400, detail='Монета уже в списке')
    return item


@router.delete('/{coin_id}', status_code=204)
async def remove_from_watchlist(
    coin_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await db.scalar(
        select(WatchlistItem).where(
            WatchlistItem.user_id == current_user.id,
            WatchlistItem.coin_id == coin_id
        )
    )

    if not item:
        raise HTTPException(status_code=404, detail='Монета не в списке')
    await db.delete(item)
    await db.commit()


@router.get('/dashboard', response_model=list[CoinMarket])
async def dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.scalars(
        select(WatchlistItem).where(WatchlistItem.user_id == current_user.id)
    )
    coin_ids = [item.coin_id for item in result.all()]

    return await get_coins_market_data(coin_ids)