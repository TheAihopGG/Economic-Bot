from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime

from .base import Base
from .mixins import IDMixin


class User(Base, IDMixin):
    __tablename__ = "users"

    guild_id: Mapped[int] = mapped_column(nullable=False)
    discord_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    balance: Mapped[int] = mapped_column(nullable=False, default=0)
    last_reward_date: Mapped[datetime] = mapped_column(default=datetime(year=1, month=1, day=1, second=1))


__all__ = ("User",)
