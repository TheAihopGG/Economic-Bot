from sqlalchemy.orm import declared_attr, Mapped, mapped_column


class IDMixin:
    @declared_attr
    def id(cls) -> Mapped[int]:
        return mapped_column(primary_key=True, index=True)


class GuildIDMixin:
    _is_unique = False

    @declared_attr
    def guild_id(cls) -> Mapped[int]:
        return mapped_column(unique=cls._is_unique, nullable=False)


__all__ = ("IDMixin",)
