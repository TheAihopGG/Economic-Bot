from datetime import datetime, timedelta
from disnake import Member, TextChannel

from ...core.base_embeds import SuccessEmbed, ErrorEmbed, InfoEmbed
from ...core.models import User


class RewardsEnabledEmbed(SuccessEmbed):
    def __init__(self):
        super().__init__(description="Награды включены.")


class RewardsDisabledEmbed(SuccessEmbed):
    def __init__(self):
        super().__init__(description="Награды выключены.")


class ShopEnabledEmbed(SuccessEmbed):
    def __init__(self):
        super().__init__(description="Магазин включен.")


class ShopDisabledEmbed(SuccessEmbed):
    def __init__(self):
        super().__init__(description="Магазин выключен.")


class RewardCostChangedEmbed(SuccessEmbed):
    def __init__(self, reward_cost: int):
        super().__init__(description=f"Сумма награды изменена. Новое значение: {reward_cost} монет.")


class RewardCostMustBeMoreThanZeroEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Сумма награды должна быть больше нуля.")


class RewardsDelayMustBeMoreThanOneEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Промежуток между наградами должен быть больше нуля.")


class ShopEventsChannelChangedEmbed(SuccessEmbed):
    def __init__(self, new_channel: TextChannel):
        super().__init__(description=f"Установлен новый канал для отслеживания событий магазина: {new_channel}.")


class RewardsDelayChangedEmbed(SuccessEmbed):
    def __init__(self, new_rewards_delay: int) -> None:
        super().__init__(description=f"Новое значение промежутка между наградами: {new_rewards_delay} секунд.")
