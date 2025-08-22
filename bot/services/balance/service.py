from sqlalchemy.ext.asyncio import AsyncSession

from ...services.users import get_or_create_user_by_discord_id


async def translate_money(
    session: AsyncSession,
    *,
    from_user_id: int,
    to_user_id: int,
    guild_id: int,
    amount: int,
) -> bool:
    from_user = await get_or_create_user_by_discord_id(
        session,
        discord_id=from_user_id,
        guild_id=guild_id,
    )
    to_user = await get_or_create_user_by_discord_id(
        session,
        discord_id=to_user_id,
        guild_id=guild_id,
    )
    await session.refresh(from_user)
    await session.refresh(to_user)
    if from_user.balance >= amount:
        from_user.balance -= amount
        to_user.balance += amount
        await session.commit()
        return True
    else:
        return False


__all__ = ("translate_money",)
