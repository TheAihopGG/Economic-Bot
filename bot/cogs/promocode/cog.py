import re
from disnake import AppCmdInter
from disnake.ext import commands

from ...core.database import session_factory
from ...services.promocodes import create_promocode, get_promocode_by_code, use_promocode, get_promocodes
from ...services.users import get_or_create_user_by_discord_id
from ...services.guilds_settings import get_or_create_guild_settings


class PromocodesCog(commands.Cog):
    @commands.slash_command()
    async def use(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def add(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def remove(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def edit(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def promocodes(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                await inter.response.send_message(
                    "\n".join(
                        [f"{promocode.code} - {promocode.bonus}" async for promocode in get_promocodes(session, guild_id=inter.guild_id)],
                    )
                    or "Нету промокодов",
                )

    @use.sub_command()
    async def use_promocode(
        self,
        inter: AppCmdInter,
        code: str,
    ) -> None:
        if inter.guild:
            async with session_factory() as session:
                user = await get_or_create_user_by_discord_id(
                    session,
                    discord_id=inter.author.id,
                    guild_id=inter.guild_id,
                )
                if not user.used_promocode_id:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        if promocode.is_active:
                            if promocode.is_infinite_usages or promocode.max_usages > promocode.usages_count:
                                await use_promocode(
                                    session,
                                    promocode=promocode,
                                    user=user,
                                )
                                await inter.response.send_message(f"Вы успешно использовали промокод")
                            else:
                                await inter.response.send_message(f"У промокода уже максимально допустимое количество использований")
                        else:
                            await inter.response.send_message(f"Промокод {promocode.code} уже не активен")
                    else:
                        await inter.response.send_message(f"Промокод не найден")
                else:
                    await inter.response.send_message(f"Вы уже использовали промокод")

    @add.sub_command()
    async def add_promocode(
        self,
        inter: AppCmdInter,
        code: str,
        bonus: int,
        max_usages: int = 0,
        is_infinite_usages: bool = True,
        is_active: bool = True,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                if re.search("^[0-9a-zA-Zа-яА-ЯеЁ]{6,20}$", code):
                    if bonus > 0:
                        if is_infinite_usages or max_usages > 0:
                            async with session_factory() as session:
                                await create_promocode(
                                    session,
                                    code=code,
                                    guild_id=inter.guild_id,
                                    bonus=bonus,
                                    max_usages=max_usages,
                                    is_infinite_usages=is_infinite_usages,
                                    is_active=is_active,
                                )
                                await inter.response.send_message("Промокод создан")
                        else:
                            await inter.response.send_message("Максимальное количество использований должно быть больше нуля")
                    else:
                        await inter.response.send_message("Бонус должен быть больше нуля")
                else:
                    await inter.response.send_message("Код промокода должен иметь длину от 6 до 20 символов")
            else:
                await inter.response.send_message("Недостаточно прав")

    @edit.sub_command()
    async def edit_promocode(
        self,
        inter: AppCmdInter,
        code: str,
        bonus: int | None = None,
        max_usages: int | None = None,
        is_infinite_usages: bool | None = None,
        is_active: bool | None = None,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        if not bonus is None:
                            if bonus > 0:
                                promocode.bonus = bonus
                            else:
                                return await inter.response.send_message("Бонус должен быть больше нуля")

                        if not max_usages is None:
                            if max_usages > 0:
                                promocode.max_usages = max_usages
                            else:
                                return await inter.response.send_message("Максимальное количество использований должно быть больше нуля")

                        if not is_infinite_usages is None:
                            promocode.is_infinite_usages = is_infinite_usages

                        if not is_active is None:
                            promocode.is_active = is_active

                        await session.commit()
                        await inter.response.send_message("Промокод обновлен")
                    else:
                        await inter.response.send_message("Промокод не найден")
            else:
                await inter.response.send_message("Недостаточно прав")

    @remove.sub_command()
    async def remove_promocode(
        self,
        inter: AppCmdInter,
        code: str,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        await session.delete(promocode)
                        await session.commit()
                        await inter.response.send_message("Промокод удалён")
                    else:
                        await inter.response.send_message("Промокод не найден")
            else:
                await inter.response.send_message("Недостаточно прав")

    @commands.slash_command()
    async def deactivate_promocode(
        self,
        inter: AppCmdInter,
        code: str,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        promocode.is_active = False
                        await session.commit()
                        await inter.response.send_message("Промокод деактивирован")
                    else:
                        await inter.response.send_message("Промокод не найден")
            else:
                await inter.response.send_message("Недостаточно прав")

    @commands.slash_command()
    async def activate_promocode(
        self,
        inter: AppCmdInter,
        code: str,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        promocode.is_active = True
                        await session.commit()
                        await inter.response.send_message("Промокод активирован")
                    else:
                        await inter.response.send_message("Промокод не найден")
            else:
                await inter.response.send_message("Недостаточно прав")


__all__ = ("PromocodesCog",)
