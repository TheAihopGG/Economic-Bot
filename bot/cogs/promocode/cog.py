import re
from disnake import AppCmdInter
from disnake.ext import commands
from disnake.ext.commands import Param

from ...core.database import session_factory
from ...core.embeds import NotEnoughPermissionsEmbed
from ...services.promocodes import create_promocode, get_promocode_by_code, use_promocode, get_promocodes
from ...services.users import get_or_create_user_by_discord_id
from .embeds import (
    PromocodeAlreadyHasMaximumUsagesCountEmbed,
    PromocodeIsNotActiveEmbed,
    PromocodeWasNotFoundEmbed,
    PromocodesListEmbed,
    YouAlreadyUsedPromocodeEmbed,
    YouSuccessfullyUsedPromocodeEmbed,
)


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

    @commands.slash_command(
        name="promocodes",
        description="Показать список промокодов",
    )
    async def promocodes(
        self,
        inter: AppCmdInter,
        show_full_info: bool = Param(
            default=False,
            description="Показать полную информацию об каждом промокоде",
        ),
    ) -> None:
        if inter.guild:
            async with session_factory() as session:
                await inter.response.send_message(
                    embed=PromocodesListEmbed(
                        promocodes=await get_promocodes(
                            session,
                            guild_id=inter.guild_id,
                        ),
                        show_full_info=show_full_info,
                    )
                )

    @use.sub_command(
        name="promocode",
        description="Использовать промокод",
    )
    async def use_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода который будет использован"),
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
                                await session.refresh(promocode)
                                await inter.response.send_message(embed=YouSuccessfullyUsedPromocodeEmbed(bonus=promocode.bonus))
                            else:
                                await inter.response.send_message(embed=PromocodeAlreadyHasMaximumUsagesCountEmbed(), ephemeral=True)
                        else:
                            await inter.response.send_message(embed=PromocodeIsNotActiveEmbed(), ephemeral=True)
                    else:
                        await inter.response.send_message(embed=PromocodeWasNotFoundEmbed(), ephemeral=True)
                else:
                    await inter.response.send_message(embed=YouAlreadyUsedPromocodeEmbed(), ephemeral=True)

    @add.sub_command(
        name="promocode",
        description="Добавить новый промокод",
    )
    async def add_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода"),
        bonus: int = Param(description="Сумма, которая зачислится участнику, который использовал этот промокод"),
        max_usages: int = Param(
            default=0,
            description="Максимальное количество использований промокода",
        ),
        is_infinite_usages: bool = Param(
            default=True,
            description="Будет ли ограничение на количество использований промокода",
        ),
        is_active: bool = Param(
            default=True,
            description="Будет ли промокод активным (неактивные промокоды нельзя использовать)",
        ),
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
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @edit.sub_command(name="promocode", description="Редактирует промокод")
    async def edit_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода, который будет отредактирован"),
        bonus: int | None = Param(
            default=None,
            description="Сумма, которая зачислится участнику, который использовал этот промокод",
        ),
        max_usages: int | None = Param(
            default=None,
            description="Максимальное количество использований промокода",
        ),
        is_infinite_usages: bool | None = Param(
            default=None,
            description="Будет ли ограничение на количество использований промокода",
        ),
        is_active: bool | None = Param(
            default=None,
            description="Будет ли промокод активным (неактивные промокоды нельзя использовать)",
        ),
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
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @remove.sub_command(
        name="promocode",
        description="Удаляет промокод",
    )
    async def remove_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода, который будет удалён"),
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
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @commands.slash_command(
        name="deactivate_promocode",
        description="Деактивирует промокод",
    )
    async def deactivate_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода, который будет деактивирован"),
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
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @commands.slash_command(name="activate_promocode", description="Активирует промокод")
    async def activate_promocode(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода, который будет деактивирован"),
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
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @commands.slash_command(name="promocode_info", description="Получить информацию о промокоде")
    async def promocode_info(
        self,
        inter: AppCmdInter,
        code: str = Param(description="Код промокода, информация о котором будет получена"),
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    if promocode := await get_promocode_by_code(
                        session,
                        code=code,
                        guild_id=inter.guild_id,
                    ):
                        await inter.response.send_message("Промокод активирован")
                    else:
                        await inter.response.send_message("Промокод не найден")
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)


__all__ = ("PromocodesCog",)
