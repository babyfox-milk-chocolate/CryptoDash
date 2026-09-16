from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


# подключение к бд через asyncgp
# echo=True печатает генерируемые запросы SQL в консоль (чисто для наглядности)
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# фабрика сессий - каждый запрос получит свою сессию 
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass