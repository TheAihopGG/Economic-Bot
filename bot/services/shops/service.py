from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from ...core.models import ShopItem


async def get_shop_item(
    session: AsyncSession,
    *,
    guild_id: int,
    role_id: int,
) -> ShopItem | None:
    return (
        await session.execute(
            select(ShopItem).where(
                ShopItem.guild_id == guild_id,
                ShopItem.role_id == role_id,
            )
        )
    ).scalar_one_or_none()


async def get_shop_items(
    session: AsyncSession,
    *,
    guild_id: int,
    return_all: bool = False,
) -> AsyncGenerator[ShopItem]:
    for item in (
        await session.execute(
            select(ShopItem).where(
                ShopItem.guild_id == guild_id,
            )
        )
    ).scalars():
        if return_all:
            yield item
        else:
            if item.is_for_sell and (item.is_infinite or item.remaining > 0):
                yield item


async def add_shop_item(
    session: AsyncSession,
    *,
    guild_id: int,
    role_id: int,
    price: int,
    remaining: int,
    is_infinite: bool,
    is_for_sell: bool = True,
) -> bool:
    if not await get_shop_item(
        session,
        guild_id=guild_id,
        role_id=role_id,
    ):
        session.add(
            ShopItem(
                guild_id=guild_id,
                role_id=role_id,
                remaining=remaining,
                price=price,
                is_infinite=is_infinite,
                is_for_sell=is_for_sell,
            )
        )
        await session.commit()
        return True
    else:
        return False


async def remove_shop_item(
    session: AsyncSession,
    *,
    guild_id: int,
    role_id: int,
) -> bool:
    return (
        await session.execute(
            delete(ShopItem).where(
                ShopItem.guild_id == guild_id,
                ShopItem.role_id == role_id,
            )
        )
    ).rowcount
