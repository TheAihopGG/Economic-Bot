from disnake import MessageInteraction, ButtonStyle, errors
from disnake.ui import View, button, Button

from ...core.database import session_factory
from ...core.models import User, ShopItem


class ConfirmPurchaseView(View):
    def __init__(
        self,
        user: User,
        shop_item: ShopItem,
    ):
        super().__init__()
        self.user = user
        self.shop_item = shop_item

    @button(style=ButtonStyle.danger, label="Подтвердить")
    async def confirm_button(self, button: Button, inter: MessageInteraction) -> None:
        if inter.author.id == self.user.discord_id:
            async with session_factory() as session:
                session.add(self.user)
                session.add(self.shop_item)
                await session.refresh(self.user)
                await session.refresh(self.shop_item)
                if self.shop_item.is_for_sell:
                    if self.shop_item.remaining > 0 or self.shop_item.is_infinite:
                        if self.user.balance >= self.shop_item.price:
                            if role := inter.guild.get_role(self.shop_item.role_id):
                                if not role in inter.author.roles:
                                    self.shop_item.remaining = min(self.shop_item.remaining, max(0, self.shop_item.remaining - 1))
                                    self.user.balance -= self.shop_item.price
                                    try:
                                        await inter.author.add_roles(role)
                                    except errors.Forbidden:
                                        await inter.response.send_message("У бота нету права на выдачу этой роли")
                                        await session.rollback()
                                    else:
                                        await session.commit()
                                        await inter.response.send_message("Вы успешно купили роль")
                                else:
                                    await inter.response.send_message("У вас уже есть эта роль")
                            else:
                                await inter.response.send_message("Роль не найдена, возможна она снята с продажи или удалена")
                        else:
                            await inter.response.send_message("Недостаточно монет для покупки роли")
                    else:
                        await inter.response.send_message("Все раскупили бл")
                else:
                    await inter.response.send_message("Роль не продаётся")
