from datetime import timedelta
from disnake import AppCmdInter, TextChannel
from disnake.ext.commands import Param
from disnake.ext import commands

from ...services.guilds_settings import get_or_create_guild_settings
from ...core.embeds import NotEnoughPermissionsEmbed
from ...core.database import session_factory
from .embeds import (
    RewardCostChangedEmbed,
    RewardCostMustBeMoreThanZeroEmbed,
    RewardsDelayChangedEmbed,
    RewardsDelayMustBeMoreThanOneEmbed,
    RewardsDisabledEmbed,
    RewardsEnabledEmbed,
    ShopDisabledEmbed,
    ShopEnabledEmbed,
    ShopEventsChannelChangedEmbed,
)


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

    @enable.sub_command(
        name="rewards",
        description="Включить награды за нахождение на сервере",
    )
    async def enable_rewards(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_rewards_enabled = True
                    await session.commit()
                    await inter.response.send_message(embed=RewardsEnabledEmbed())
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @disable.sub_command(
        name="rewards",
        description="Выключить награды за нахождение на сервере",
    )
    async def disable_rewards(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_rewards_enabled = False
                    await session.commit()
                    await inter.response.send_message(embed=RewardsDisabledEmbed())
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @enable.sub_command(
        name="shop",
        description="Включить магазин на сервере",
    )
    async def enable_shop(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_shop_enabled = True
                    await session.commit()
                    await inter.response.send_message(embed=ShopEnabledEmbed())
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @disable.sub_command(
        name="shop",
        description="Выключить магазин на сервере",
    )
    async def disable_shop(self, inter: AppCmdInter) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.is_shop_enabled = False
                    await session.commit()
                    await inter.response.send_message(embed=ShopDisabledEmbed())
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)

    @set.sub_command(
        name="reward_cost",
        description="Установить новую сумму награды за нахождение на сервере",
    )
    async def reward_cost(
        self,
        inter: AppCmdInter,
        cost: int = Param(description="Новая сумма награды"),
    ) -> None:
        if inter.guild:
            if cost > 0:
                if inter.author.guild_permissions.administrator:
                    async with session_factory() as session:
                        guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                        await session.refresh(guild_settings)
                        guild_settings.reward_cost = cost
                        await session.commit()
                        await inter.response.send_message(embed=RewardCostChangedEmbed(reward_cost=cost))
                else:
                    await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)
            else:
                await inter.response.send_message(embed=RewardCostMustBeMoreThanZeroEmbed(), ephemeral=True)

    @set.sub_command(
        name="rewards_delay",
        description="Установить новую задержку между наградами за нахождение на сервере",
    )
    async def rewards_delay(
        self,
        inter: AppCmdInter,
        delay: int = Param(description="Новая задержка для наград за нахождение на сервере"),
    ) -> None:
        if inter.guild:
            if delay > 0:
                if inter.author.guild_permissions.administrator:
                    async with session_factory() as session:
                        guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                        await session.refresh(guild_settings)
                        guild_settings.reward_delay = timedelta(seconds=delay)
                        await session.commit()
                        await inter.response.send_message(embed=RewardsDelayChangedEmbed(new_rewards_delay=delay))
                else:
                    await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)
            else:
                await inter.response.send_message(embed=RewardsDelayMustBeMoreThanOneEmbed(), ephemeral=True)

    # TODO: заготовка на будущее
    @set.sub_command(
        name="shop_events_channel",
        description="Установить новый канал для событий магазина",
    )
    async def shop_events_channel(
        self,
        inter: AppCmdInter,
        channel: TextChannel = Param(description="Новый канал для событий магазина"),
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                async with session_factory() as session:
                    guild_settings = await get_or_create_guild_settings(session, guild_id=inter.guild_id)
                    await session.refresh(guild_settings)
                    guild_settings.shop_events_channel_id = channel.id
                    await session.commit()
                    await inter.response.send_message(embed=ShopEventsChannelChangedEmbed(new_channel=channel), ephemeral=True)
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)


__all__ = ("GuildSettingsCog",)
