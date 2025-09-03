from typing import Iterator

from disnake import Role

from ...core.base_embeds import SuccessEmbed, InfoEmbed, ErrorEmbed
from ...core.models import ShopItem


class ShopEmbed(InfoEmbed):
    def __init__(self, shop_items: Iterator[ShopItem]):
        super().__init__(
            description="Список товаров:" + [f"\n<@&{shop_item.role_id}> - {shop_item.price} :coin:\n{shop_item.description}" for shop_item in shop_items],
        )


class ShopIsDisabledEmbed(ErrorEmbed):
    def __init__(self) -> None:
        super().__init__(description="Магазин выключен на этом сервере.")


class RoleWasAddedToShop(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description="Роль добавлена в магазин сервера.")


class RoleWasAlreadyAddedToShop(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description="Эта роль уже добавлена в магазин сервера.")


class RemainingCantBeLessThanZeroEmbed(ErrorEmbed):
    def __init__(self) -> None:
        super().__init__(description="Количество товара не может быть меньше нуля.")


class PriceMustBeMoreThanZeroEmbed(ErrorEmbed):
    def __init__(self) -> None:
        super().__init__(description="Цена должна быть больше нуля.")


class RoleWasDeletedFromShopEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description="Роль удалена из магазина сервера.")


class RoleWasNotFoundInShopEmbed(ErrorEmbed):
    def __init__(self) -> None:
        super().__init__(description="Роль не найдена в магазине сервера.")


class ItemDescriptionMustIsToLongEmbed(ErrorEmbed):
    def __init__(self) -> None:
        super().__init__(description="Описание может быть длиной от 0 до 200 символов.")


class ShopItemUpdatedEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description="Товар обновлён")


class BotCantGiveARoleEmbed(ErrorEmbed):
    def __init__(self, role: Role) -> None:
        super().__init__(description=f"Бот не может выдать роль {role.mention}. Обратитесь к администратор сервера.")


class YouAlreadyHasTheRoleEmbed(SuccessEmbed):
    def __init__(self, role: Role) -> None:
        super().__init__(description=f"Вы купили роль {role.mention}")


class YouAlreadyHasTheRoleEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description=f"У вас уже есть эта роль")


class NotEnoughMoneyToBuyRoleEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description=f"У вас недостаточно монет чтобы купить эту роль")


class RoleIsSoldOutEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description=f"Роль раскуплена")


class RoleIsNotForSaleEmbed(SuccessEmbed):
    def __init__(self) -> None:
        super().__init__(description=f"Роль не продаётся")


class AreYouSureToBuyRoleEmbed(InfoEmbed):
    def __init__(self, role: Role) -> None:
        super().__init__(description=f"Вы уверены, что хотите купить роль {role.mention}?")
