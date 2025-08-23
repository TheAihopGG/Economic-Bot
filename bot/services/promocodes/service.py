from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ...core.models import Promocode, User


async def create_promocode(
    session: AsyncSession,
    *,
    code: str,
    guild_id: int,
    bonus: int,
    max_usages: int = 0,
    is_infinite_usages: bool = True,
    is_active: bool = True,
) -> bool:
    if (
        await get_promocode_by_code(
            session,
            code=code,
            guild_id=guild_id,
        )
        is None
    ):
        session.add(
            Promocode(
                guild_id=guild_id,
                bonus=bonus,
                code=code,
                max_usages=max_usages,
                is_infinite_usages=is_infinite_usages,
                is_active=is_active,
            )
        )
        await session.commit()
        return True
    else:
        return False


async def get_promocode_by_code(
    session: AsyncSession,
    *,
    code: str,
    guild_id: int,
) -> Promocode | None:
    return (
        await session.execute(
            select(Promocode).where(
                Promocode.guild_id == guild_id,
                Promocode.code == code,
            )
        )
    ).scalar_one_or_none()


async def use_promocode(
    session: AsyncSession,
    *,
    user: User,
    promocode: Promocode,
) -> None:
    promocode.usages_count += 1
    user.used_promocode_id = promocode.id
    user.balance += promocode.bonus
    await session.commit()


async def get_promocodes(
    session: AsyncSession,
    *,
    guild_id: int,
) -> AsyncGenerator[Promocode]:
    for promocode in (
        await session.execute(
            select(Promocode).where(
                Promocode.guild_id == guild_id,
            )
        )
    ).scalars():
        yield promocode
