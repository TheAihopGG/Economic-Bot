from sqlalchemy.orm import mapped_column, Mapped
from datetime import timedelta

from .base import Base
from .mixins import GuildIDMixin


class GuildSettings(Base, GuildIDMixin):
    __tablename__ = "guilds_settings"
    _is_unique = True
    shop_events_channel_id: Mapped[int] = mapped_column(nullable=True)
    reward_delay: Mapped[timedelta] = mapped_column(default=timedelta(seconds=10))
    reward_cost: Mapped[int] = mapped_column(nullable=False, default=100)
    is_rewards_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_shop_enabled: Mapped[bool] = mapped_column(nullable=False, default=True)


__all__ = ("GuildSettings",)
