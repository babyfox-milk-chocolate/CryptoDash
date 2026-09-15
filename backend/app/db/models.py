from datetime import datetime
from sqlalchemy import String, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # связь один ко многим: у пользователя много монет в watchlist
    watchlist: Mapped[list['WatchlistItem']] = relationship(
        back_populates='user', cascade='all, delete-orphan'
    )


class WatchlistItem(Base):
    __tablename__ = 'watchlist_items'
    # один пользователь не может добавить две одинаковые монеты 
    __table_args__ = (UniqueConstraint('user_id', 'coin_id', name='uq_user_coin'),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    coin_id: Mapped[int] = mapped_column(String(100))
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped['User'] = relationship(back_populates='watchlist')
    