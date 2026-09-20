import pytest 
from unittest.mock import AsyncMock
import httpx

from app.db.models import WatchlistItem


class TestWathlistCRUD:
    async def test_add_coin(self, auth_client):
        resp = await auth_client.post('/api/watchlist', json={'coin_id': 'bitcoin'})
        assert resp.status_code == 201
        assert resp.json()['coin_id'] == 'bitcoin'

    async def test_add_duplicate_coin(self, auth_client):
        await auth_client.post('/api/watchlist', json={'coin_id': 'bitcoin'})
        resp = await auth_client.post('/api/watchlist', json={'coin_id': 'bitcoin'})
        assert resp.status_code == 400 # UniqueConstrant

    async def test_list_own_coins(self, auth_client):
        await auth_client.post("/api/watchlist", json={"coin_id": "bitcoin"})
        await auth_client.post("/api/watchlist", json={"coin_id": "ethereum"})
        resp = await auth_client.get('/api/watchlist')
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_remove_coin(self, auth_client):
        await auth_client.post('/api/watchlist', json={'coin_id': 'bitcoin'})
        resp = await auth_client.delete('/api/watchlist/bitcoin')
        assert resp.status_code == 204

    async def test_remove_nonexistent_coin(self, auth_client):
        resp = await auth_client.delete('/api/watchlist/asdasd')
        assert resp.status_code == 404


class TestWatchlistIsolation:
    # пользователь видит только свои монеты 
    async def test_list_excludes_others_coins(self, client, db_session, user_a, user_b):
        db_session.add(WatchlistItem(user_id=user_b.id, coin_id='dogecoin'))
        await db_session.commit()

        from app.core.security import create_access_token
        client.headers['Authorization'] = f'Bearer {create_access_token(user_a.id)}'
        resp = await client.get('/api/watchlist')
        assert resp.status_code == 200
        coin_ids = [item['coin_id'] for item in resp.json()]
        assert 'dogecoin' not in coin_ids

    async def test_cannot_delete_others_coin(self, client, db_session, user_a, user_b):
        db_session.add(WatchlistItem(user_id=user_b.id, coin_id="dogecoin"))
        await db_session.commit()

        from app.core.security import create_access_token
        client.headers["Authorization"] = f"Bearer {create_access_token(user_a.id)}"
        resp = await client.delete("/api/watchlist/dogecoin")
        assert resp.status_code == 404  # для Alice её не существует

        from sqlalchemy import select
        item = await db_session.scalar(
            select(WatchlistItem).where(WatchlistItem.coin_id == "dogecoin")
        )
        assert item is not None

    
class TestDashboard:
    async def test_dash_with_mocked_api(self, auth_client, monkeypatch):
        # подменяем вызов API этими данными (дабы избежать 429)
        data = [
            {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin',
             'current_price': 67000, 'price_change_percentage_24h': 2.5, 
             'market_cap': 1_300_300, 'image': 'http://img/btc.png'},
        ]
        mock = AsyncMock(return_value=data)
        monkeypatch.setattr("app.api.routes.watchlist.get_coins_market_data", mock)

        await auth_client.post("/api/watchlist", json={"coin_id": "bitcoin"})
        resp = await auth_client.get("/api/watchlist/dashboard")

        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["current_price"] == 67000
        mock.assert_awaited_once()  # убедились, что сервис вызвали