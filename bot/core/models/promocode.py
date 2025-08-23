from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import String

from .base import Base
from .mixins import IDMixin, GuildIDMixin


class Promocode(
    Base,
    IDMixin,
    GuildIDMixin,
):
    __tablename__ = "promocodes"
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    max_usages: Mapped[int] = mapped_column(nullable=True)
    usages_count: Mapped[int] = mapped_column(nullable=False, default=0)
    bonus: Mapped[int]
    is_infinite_usages: Mapped[bool] = mapped_column(default=True)
    is_active: Mapped[bool] = mapped_column(default=True)


__all__ = ("Promocode",)
