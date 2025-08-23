from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import String

from .base import Base
from .mixins import IDMixin, GuildIDMixin


class ShopItem(
    Base,
    IDMixin,
    GuildIDMixin,
):
    __tablename__ = "shops_items"
    role_id: Mapped[int] = mapped_column(nullable=False, unique=True)
    price: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Нет описания",
    )
    remaining: Mapped[int] = mapped_column(nullable=False)
    is_for_sell: Mapped[bool] = mapped_column(nullable=False, default=True)
    is_infinite: Mapped[bool] = mapped_column(nullable=False, default=True)


__all__ = ("ShopItem",)
