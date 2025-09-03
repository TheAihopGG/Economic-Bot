from disnake import AppCmdInter, Member
from disnake.ext import commands
from disnake.ext.commands import Param
from datetime import datetime

from ...services.balance import translate_money
from ...services.users import get_or_create_user_by_discord_id, get_baltop_users
from ...services.guilds_settings import get_or_create_guild_settings
from ...core.database import session_factory
from ...core.embeds import NotEnoughPermissionsEmbed
from .embeds import (
    BalTopEmbed,
    RewardsIsDisabledOnGuildEmbed,
    YouAlreadyGotRewardNextInEmbed,
    YouCantPay2BotEmbed,
    YouCantPayYourselfEmbed,
    YouCantPayLessThanEmbed,
    YouGotRewardEmbed,
    YouSuccessfullyAwardedMoneyEmbed,
    YouSuccessfullyPaidEmbed,
    YourBalanceEmbed,
)
from .views import ConfirmMoneyPayView


class EconomicCog(commands.Cog):
    @commands.slash_command(
        name="pay",
        description="Перевести деньги.",
    )
    async def pay(
        self,
        inter: AppCmdInter,
        to_member: Member = Param(description="Участник, которому будут переведены монеты."),
        amount: int = Param(description="Сумма монет, которая будет переведена."),
        confirm: bool = Param(
            default=False,
            description="Запрашивать подтверждение операции или нет.",
        ),
    ) -> None:
        if inter.guild:
            if not to_member.bot:
                if not to_member.id == inter.author.id:
                    if amount >= 5:
                        if confirm:
                            await inter.response.send_message(
                                "Вы уверены что хотите перевести деньги?",
                                view=ConfirmMoneyPayView(
                                    from_user=inter.author,
                                    to_user=to_member,
                                    amount=amount,
                                ),
                                ephemeral=True,
                            )
                        else:
                            async with session_factory() as session:
                                await translate_money(
                                    session,
                                    from_user_id=inter.author.id,
                                    to_user_id=to_member.id,
                                    amount=amount,
                                    guild_id=inter.guild_id,
                                )
                                await inter.response.send_message(embed=YouSuccessfullyPaidEmbed())
                    else:
                        await inter.response.send_message(embed=YouCantPayLessThanEmbed(), ephemeral=True)
                else:
                    await inter.response.send_message(embed=YouCantPayYourselfEmbed(), ephemeral=True)
            else:
                await inter.response.send_message(embed=YouCantPay2BotEmbed(), ephemeral=True)

    @commands.slash_command(
        name="balance",
        description="Посмотреть баланс участника",
    )
    async def balance(self, inter: AppCmdInter, member: Member | None = None) -> None:
        if inter.guild:
            member = member or inter.author
            async with session_factory() as session:
                user = await get_or_create_user_by_discord_id(
                    session,
                    discord_id=member.id,
                    guild_id=inter.guild_id,
                )
                await session.refresh(user)
                await inter.response.send_message(embed=YourBalanceEmbed(balance=user.balance))

    @commands.slash_command()
    async def get(self, inter: AppCmdInter) -> None:
        pass

    @get.sub_command(
        name="reward",
        description="Получить награду нза нахождение на севере",
    )
    async def reward(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                user = await get_or_create_user_by_discord_id(
                    session,
                    discord_id=inter.author.id,
                    guild_id=inter.guild_id,
                )
                guild_settings = await get_or_create_guild_settings(
                    session,
                    guild_id=inter.guild_id,
                )
                await session.refresh(guild_settings)
                await session.refresh(user)
                if guild_settings.is_rewards_enabled:
                    if user.last_reward_date + guild_settings.reward_delay < datetime.now():
                        earned_money = guild_settings.reward_cost
                        user.balance += earned_money
                        user.last_reward_date = datetime.now()
                        await session.commit()
                        await session.refresh(guild_settings)
                        await inter.response.send_message(embed=YouGotRewardEmbed(amount=earned_money, reward_delay=guild_settings.reward_delay))
                    else:
                        await inter.response.send_message(
                            embed=YouAlreadyGotRewardNextInEmbed(last_reward_date=user.last_reward_date, reward_delay=guild_settings.reward_delay),
                            ephemeral=True,
                        )
                else:
                    await inter.response.send_message(embed=RewardsIsDisabledOnGuildEmbed(), ephemeral=True)

    @commands.slash_command(
        name="baltop",
        description="Посмотреть топ по балансу",
    )
    async def baltop(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                await inter.response.send_message(
                    embed=BalTopEmbed(
                        baltop=await get_baltop_users(
                            session,
                            guild_id=inter.guild_id,
                        ),
                    ),
                    ephemeral=True,
                )

    @commands.slash_command(
        name="award",
        description="Выдать деньги",
    )
    async def award(
        self,
        inter: AppCmdInter,
        to_member: Member,
        amount: int,
    ) -> None:
        if inter.guild:
            if inter.author.guild_permissions.administrator:
                if not to_member.bot:
                    async with session_factory() as session:
                        user = await get_or_create_user_by_discord_id(
                            session,
                            discord_id=to_member.id,
                            guild_id=inter.guild_id,
                        )
                        await session.refresh(user)
                        user.balance += amount
                        await session.commit()
                        await inter.response.send_message(
                            embed=YouSuccessfullyAwardedMoneyEmbed(
                                amount=amount,
                                to=to_member,
                            )
                        )
                else:
                    await inter.response.send_message(embed=YouCantPay2BotEmbed(), ephemeral=True)
            else:
                await inter.response.send_message(embed=NotEnoughPermissionsEmbed(), ephemeral=True)


__all__ = ("EconomicCog",)
