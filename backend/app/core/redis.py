import redis.asyncio as aioredis
from app.core.config import settings

# async-клиент Redis, decode_responses - чтобы получать str, а не bytes
redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
