import pytest
from sqlalchemy import select 
from app.db.models import User


class TestRegistration:
    async def test_register_success(self, client):
        resp = await client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'some@mail.com',
            'password': 'securepass123'
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data['username'] == 'newuser'
        assert 'hashed_password' not in data

    async def test_password_is_hashed(self, client, db_session):
        resp = await client.post('/api/auth/register', json={
            "username": "newuser", "password": "securepass",
        })
        user = await db_session.scalar(select(User).where(User.username == 'newuser'))
        assert user.hashed_password != 'securepass'

    async def test_register_duplicate_username(self, client, user_a):
        resp = await client.post('/api/auth/register', json={
            "username": "user1", "password": "securepass",
        })
        assert resp.status_code == 400


class TestLogin:
    async def test_login_returns_tokens(self, client, user_a):
        resp = await client.post('/api/auth/login', json={
            'username': 'user1', 'password': 'pass12345'
        })
        assert resp.status_code == 200
        data = resp.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    async def test_login_wrong_password(self, client):
        resp = await client.post('/api/auth/login', json={
            'username': 'user1', 'password': 'wrongpassword'
        })
        assert resp.status_code == 401


class TestTokens:
    async def test_refesh_returns_new_pair(self, client, user_a):
        login = await client.post('/api/auth/login', json={
            'username': 'user1', 'password': 'pass12345'
        })
        refresh = login.json()['refresh_token']
        resp = await client.post('/api/auth/refresh', json={'refresh_token': refresh})
        assert resp.status_code == 200
        assert 'access_token' in resp.json()

    async def test_access_token_rejected_as_refresh(self, client, user_a):
        login = await client.post("/api/auth/login", json={
            "username": "user1", "password": "pass12345",
        })
        access = login.json()["access_token"]
        resp = await client.post("/api/auth/refresh", json={"refresh_token": access})
        assert resp.status_code == 401


class TestProtectedAccess:
    async def test_no_token_denied(self, client):
        resp = await client.get('/api/watchlist')
        assert resp.status_code in (401, 403)

    async def test_with_token_allowed(self, auth_client):
        resp = await auth_client.get('/api/watchlist')
        assert resp.status_code == 200

    async def test_returns_current_user(self, auth_client):
        resp = await auth_client.get('/api/auth/me')
        assert resp.status_code == 200
        assert resp.json()['username'] == 'user1'
    