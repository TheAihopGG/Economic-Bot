from datetime import datetime, timedelta
from disnake import AppCmdInter
from disnake.ext import commands

from ...services.guilds_settings import get_guild_settings
from ...core.database import session_factory


class GuildSettingsCog(commands.Cog):
    @commands.slash_command()
    async def set(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def enable(self, inter: AppCmdInter) -> None:
        pass

    @commands.slash_command()
    async def disable(self, inter: AppCmdInter) -> None:
        pass

    @enable.sub_command()
    async def enable_rewards(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_rewards_enabled = True
                    await session.commit()
                    await inter.response.send_message("Ежедневные награды включены")
            else:
                await inter.response.send_message("Недостаточно прав")

    @disable.sub_command(name="rewards")
    async def disable_rewards(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_rewards_enabled = False
                    await session.commit()
                    await inter.response.send_message("Ежедневные награды выключены")
            else:
                await inter.response.send_message("Недостаточно прав")

    @set.sub_command(name="rewards")
    async def reward_cost(
        self,
        inter: AppCmdInter,
        cost: int,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.reward_cost = cost
                    await session.commit()
                    await inter.response.send_message("Успешно")
            else:
                await inter.response.send_message("Недостаточно прав")

    @set.sub_command()
    async def rewards_delay(
        self,
        inter: AppCmdInter,
        delay: int,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.reward_delay = timedelta(seconds=delay)
                    await session.commit()
                    await inter.response.send_message("Успешно")
            else:
                await inter.response.send_message("Недостаточно прав")


__all__ = ("GuildSettingsCog",)
