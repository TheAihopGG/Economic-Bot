from disnake import AppCmdInter, Member
from disnake.ext import commands
from datetime import datetime

from sqlalchemy import select

from ...services.balance import translate_money
from ...services.users import get_or_create_user_by_discord_id
from ...services.guilds_settings import get_or_create_guild_settings
from ...core.database import session_factory
from ...core.models import User
from .views import ConfirmMoneyPayView


class EconomicCog(commands.Cog):
    @commands.slash_command()
    async def pay(
        self,
        inter: AppCmdInter,
        to_member: Member,
        amount: int,
        confirm: bool = False,
    ) -> None:
        if inter.guild:
            if not to_member.bot:
                if not to_member.id == inter.author.id:
                    if amount > 5:
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
                                await inter.response.send_message("Вы успешно перевели деньги")
                    else:
                        await inter.response.send_message("Вы не можете отправить меньше 6 монет")
                else:
                    await inter.response.send_message("You cant pay yourself")
            else:
                await inter.response.send_message("Вы не можете перевести деньги боту")

    @commands.slash_command()
    async def balance(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                user = await get_or_create_user_by_discord_id(
                    session,
                    discord_id=inter.author.id,
                    guild_id=inter.guild_id,
                )
                await session.refresh(user)
                await inter.response.send_message(f"{user.balance}")

    @commands.slash_command()
    async def get(self, inter: AppCmdInter) -> None:
        pass

    @get.sub_command()
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
                        await inter.response.send_message(f"Вы заработали {earned_money}")
                    else:
                        await inter.response.send_message(f"Вы сможете ещё раз получить награду через <t:{int((user.last_reward_date + guild_settings.reward_delay).timestamp())}:R>")
                else:
                    await inter.response.send_message("Ежедневные награды отключены на этом сервере")

    @commands.slash_command()
    async def top(self, inter: AppCmdInter) -> None:
        if inter.guild:
            async with session_factory() as session:
                await inter.response.send_message(
                    "\n".join(
                        [
                            f"{number}. <@{user.discord_id}> - {user.balance}"
                            for number, user in enumerate(
                                (await session.execute(list(select(User).where(User.guild_id == inter.guild_id).order_by(User.balance).limit(10)).reverse())).scalars(),
                                start=1,
                            )
                        ]
                    ),
                    ephemeral=True,
                )

    @commands.slash_command()
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
                        await inter.response.send_message("Вы выдали деньги")
                else:
                    await inter.response.send_message("Вы не можете перевести деньги боту")
            else:
                await inter.response.send_message("Недостаточно прав")


__all__ = ("EconomicCog",)
