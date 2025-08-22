from typing import Iterable, Iterator
from disnake import Button, ButtonStyle, MessageInteraction, Member
from disnake.ui import View, button
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.models import User
from ...core.database import session_factory
from ...services.balance import translate_money


class ConfirmMoneyPayView(View):
    def __init__(self, from_user: Member, to_user: Member, amount: int) -> None:
        super().__init__(timeout=60)
        self.from_user = from_user
        self.to_user = to_user
        self.amount = amount

    @button(style=ButtonStyle.danger, label="Подтвердить")
    async def confirm(self, button: Button, inter: MessageInteraction) -> None:
        if inter.author.id == self.from_user.id:
            async with session_factory() as session:
                await translate_money(
                    session,
                    from_user_id=self.from_user.id,
                    to_user_id=self.to_user.id,
                    amount=self.amount,
                    guild_id=inter.guild_id,
                )
                await inter.response.send_message("Вы успешно перевели деньги")


__all__ = ("ConfirmMoneyPayView",)
