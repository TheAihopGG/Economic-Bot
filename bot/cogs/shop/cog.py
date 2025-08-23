import re
from disnake import AppCmdInter, Role
from disnake.ext import commands

from ...services.shops import get_shop_items, add_shop_item, remove_shop_item, get_shop_item
from ...services.users import get_or_create_user_by_discord_id
from ...services.guilds_settings import get_or_create_guild_settings
from ...core.database import session_factory
from .views import ConfirmPurchaseView


class ShopCog(commands.Cog):
    @commands.slash_command()
    async def shop(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                if guild_settings.is_shop_enabled:
                    await inter.response.send_message(
                        "\n".join(
                            [
                                f"<@&{shop_item.role_id}> - {shop_item.price} монет"
                                async for shop_item in get_shop_items(
                                    session,
                                    guild_id=inter.guild_id,
                                )
                            ]
                        )
                        or "Нету товаров",
                        ephemeral=True,
                    )
                else:
                    await inter.response.send_message(
                        "Магазин выключен на этом сервере",
                        ephemeral=True,
                    )

    @commands.slash_command()
    async def add_shop_item(
        self,
        inter: AppCmdInter,
        role: Role,
        price: int,
        remaining: int = 0,
        is_infinite: bool = True,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                if price > 1:
                    if is_infinite or remaining > -1:
                        async with session_factory() as session:
                            if await add_shop_item(
                                session,
                                guild_id=inter.guild_id,
                                role_id=role.id,
                                remaining=remaining,
                                price=price,
                                is_infinite=is_infinite,
                            ):
                                await inter.response.send_message("Роль добавлена в магазин сервера")
                            else:
                                await inter.response.send_message("Эта роль уже добавлена в магазин сервера")
                    else:
                        await inter.response.send_message("remaining не может быть меньше нуля")
                else:
                    await inter.response.send_message("Цена должна быть больше 1 монеты")
            else:
                await inter.response.send_message("Недостаточно прав")

    @commands.slash_command()
    async def remove_shop_item(
        self,
        inter: AppCmdInter,
        role: Role,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if await remove_shop_item(
                        session,
                        guild_id=inter.guild_id,
                        role_id=role.id,
                    ):
                        await inter.response.send_message("Роль удалена из магазина сервера")
                    else:
                        await inter.response.send_message("Роль не найдена в магазине сервера")
            else:
                await inter.response.send_message("Недостаточно прав")

    @commands.slash_command()
    async def edit_shop_item(
        self,
        inter: AppCmdInter,
        role: Role,
        remaining: int | None = None,
        price: int | None = None,
        description: str | None = None,
        is_infinite: bool | None = None,
        is_for_sell: bool | None = None,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if shop_item := await get_shop_item(
                        session,
                        guild_id=inter.guild_id,
                        role_id=role.id,
                    ):
                        if not remaining is None:
                            if remaining < 0:
                                await inter.response.send_message("remaining не может быть меньше нуля")
                            else:
                                shop_item.remaining = remaining

                        if not price is None:
                            if price > 1:
                                shop_item.price = price
                            else:
                                await inter.response.send_message("Цена должна быть больше 1 монеты")

                        if not description is None:
                            if re.search("^[.]{0,200}$", description, re.S):
                                shop_item.description = description
                            else:
                                await inter.response.send_message("Описание может быть длиной от 0 до 200 символов")

                        if not is_infinite is None:
                            shop_item.is_infinite = is_infinite

                        if not is_for_sell is None:
                            shop_item.is_for_sell = is_for_sell

                        await session.commit()

                        await inter.response.send_message("Роль обновлена")
                    else:
                        await inter.response.send_message("Роль не найдена в магазине сервера")
            else:
                await inter.response.send_message("Недостаточно прав")

    @commands.slash_command()
    async def buy_shop_item(
        self,
        inter: AppCmdInter,
        role: Role,
    ) -> None:
        if inter.guild:
            async with session_factory() as session:
                guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                if guild_settings.is_shop_enabled:
                    user = await get_or_create_user_by_discord_id(
                        session,
                        discord_id=inter.author.id,
                        guild_id=inter.guild_id,
                    )
                    if shop_item := await get_shop_item(
                        session,
                        guild_id=inter.guild_id,
                        role_id=role.id,
                    ):
                        await inter.response.send_message(view=ConfirmPurchaseView(user=user, shop_item=shop_item))
                else:
                    await inter.response.send_message(
                        "Магазин выключен на этом сервере",
                        ephemeral=True,
                    )


__all__ = ("ShopCog",)
