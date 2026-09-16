import json
import httpx
import asyncio
from app.core.redis import redis_client


BASE_URL = "https://api.coingecko.com/api/v3"
CACHE_TTL = 60


async def get_coins_market_data(coin_ids: list[str]) -> list[dict]:
    ''' 
    возвращаем рыночные данные по списку монет
    проверяем кэш, недостающие - тянем из API одним запросом
    '''

    if not coin_ids:
        return []

    cache_key = f"market:{','.join(sorted(coin_ids))}"
    # пробуем достать из redis 
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached) 

    # если нет в redis - обращаемся к API
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f"{BASE_URL}/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ",".join(coin_ids),
                "order": "market_cap_desc"
            },
        )
        resp.raise_for_status()
        data = resp.json()

    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL)
    return data


async def get_coin_history(coin_id: str, days: int = 7) -> dict:
    '''  
        получаем историю цены монеты за N дней
    '''
    cache_key = f'history:{coin_id}:{days}'
    cached = await redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(
            f'{BASE_URL}/coins/{coin_id}/market_chart',
            params={'vs_currency': 'usd', 'days': days}
        )
        resp.raise_for_status()
        data = resp.json()

    await redis_client.set(cache_key, json.dumps(data), ex=CACHE_TTL)
    return data


async def get_coin_full(coin_id: str, days: int = 7) -> dict:
    '''
        рыночные данные + история - парралельно через gather 
    '''
    # запускаем обе корутины одновременно 
    market, history = await asyncio.gather(
        get_coins_market_data([coin_id]),
        get_coin_history(coin_id, days)
    )

    return {
        'market': market[0] if market else None,
        'history': history
    }

    

