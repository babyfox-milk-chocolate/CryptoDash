# CryptoDash.IO

> Персональный трекер криптовалют: watchlist с живыми ценами, графики истории и параллельная агрегация данных из CoinGecko. Backend на FastAPI (полностью async), frontend на Vue 3, кэш на Redis — всё в Docker.

<!-- Замени плейсхолдеры на свои значения -->
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0_async-D71F00?logo=sqlalchemy&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-3-4FC08D?logo=vue.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

![alt text](image.png)

---

##  Возможности

- **JWT-аутентификация** — access + refresh токены, реализованные вручную (хеширование bcrypt, подпись через python-jose)
- **Watchlist** — персональный список монет с изоляцией данных: каждый пользователь видит только свои
- **Дашборд** — живые цены, изменение за 24ч и капитализация, с автообновлением каждую минуту
- **Графики истории цен** — по клику на монету, данные за 30 дней
- **Параллельная агрегация** — данные из CoinGecko собираются асинхронно через `asyncio.gather`
- **Кэширование на Redis** — TTL-кэш поверх внешнего API снижает нагрузку и обходит rate limit

---

## Замеры скорости 

Главная причина выбрать FastAPI здесь — асинхронный сбор данных из внешнего API. Когда нужно получить несколько независимых ресурсов (рыночные данные + история цен), последовательные запросы ждут друг друга, а `asyncio.gather` выполняет их одновременно:

| Подход | Время |
|--------|-------|
| Последовательно (`await` подряд) | ~6.3 с |
| Параллельно (`asyncio.gather`) | ~0.7 с |

---


## Стек технологий

**Backend:** FastAPI · SQLAlchemy 2.0 (async) · Pydantic v2 · Alembic · PostgreSQL · Redis · httpx · python-jose · bcrypt

**Frontend:** Vue 3 (Composition API) · Vite · Pinia · Vue Router · Axios · Tailwind CSS · Chart.js · lucide-vue-next

**Тесты:** pytest · pytest-asyncio · httpx.AsyncClient

**Инфраструктура:** Docker · Docker Compose

---

## Архитектура

```
backend/app/
├── main.py              # точка входа, подключение роутеров, CORS
├── core/                # config, security (JWT, хеширование), Redis
├── db/                  # engine, session, ORM-модели
├── schemas/             # Pydantic-схемы
├── api/
│   ├── deps.py          # зависимости: get_db, get_current_user
│   └── routes/          # эндпоинты: auth, coins, watchlist
└── services/            # async-клиент CoinGecko + кэш
```

---

##  Запуск

### 1. Клонировать

```bash
git clone https://github.com/USERNAME/CryptoDash.git
cd CryptoDash
```

### 2. Переменные окружения

```bash
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

# async-драйвер в URL: postgresql+asyncpg
DATABASE_URL=postgresql+asyncpg://usernamer:password@db:5432/db
REDIS_URL=redis://redis:port/0

SECRET_KEY=сгенерируй
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Поднять backend + Postgres + Redis

```bash
docker compose up --build
```

Применить миграции:

```bash
docker compose exec backend alembic upgrade head
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

---

##  Основные эндпоинты
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/api/auth/register` | Регистрация |
| `POST` | `/api/auth/login` | Вход (пара токенов) |
| `POST` | `/api/auth/refresh` | Обновление access-токена |
| `GET` | `/api/auth/me` | Текущий пользователь |
| `GET` | `/api/coins` | Рыночные данные по списку монет |
| `GET` | `/api/coins/{id}` | Данные монеты + история (параллельно) |
| `GET/POST` | `/api/watchlist` | Список / добавление монеты |
| `DELETE` | `/api/watchlist/{coin_id}` | Удаление из watchlist |
| `GET` | `/api/watchlist/dashboard` | Watchlist с живыми ценами |

---

## Тестирование

Бэк покрыт async-тестами (`pytest-asyncio` + `httpx.AsyncClient`). Тестовая БД — SQLite в памяти с подменой зависимости `get_db` через `dependency_overrides`; вызовы к CoinGecko изолированы моками.

Что покрыто:

- **Аутентификация** — регистрация, хеширование пароля, логин, refresh, отказ access-токену в роли refresh
- **Изоляция watchlist** — пользователь видит и удаляет только свои монеты (чужие → `404`)

---

## Планы развития

- Валидация ID монеты и автодополнение через поиск CoinGecko
- Отзыв refresh-токенов через Redis (полноценный logout)
- Production-сборка: Docker для frontend + reverse-proxy, uvicorn workers
- CI/CD через GitHub Actions


