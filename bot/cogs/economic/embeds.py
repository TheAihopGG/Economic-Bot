from datetime import datetime, timedelta
from disnake import Member

from ...core.base_embeds import SuccessEmbed, ErrorEmbed, InfoEmbed
from ...core.models import User


class YouCantPay2BotEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Вы не можете перевести деньги боту.")


class YouCantPayYourselfEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Вы не можете перевести деньги себе же.")


class YouCantPayLessThanEmbed(ErrorEmbed):
    def __init__(self, less_than: int = 5):
        super().__init__(description=f"Вы не можете перевести меньше {less_than} монет.")


class YouSuccessfullyPaidEmbed(SuccessEmbed):
    def __init__(self, amount: int, to: Member):
        super().__init__(description=f"Вы успешно перевели {amount} монет участнику {to.mention}.")


class YourBalanceEmbed(InfoEmbed):
    def __init__(self, balance: int):
        super().__init__(description=f"У вас {balance} монет.")


class RewardsIsDisabledOnGuildEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Награды отключены на этом сервере.")


class YouAlreadyGotRewardNextInEmbed(ErrorEmbed):
    def __init__(self, last_reward_date: datetime, reward_delay: timedelta):
        super().__init__(description=f"Вы сможете ещё раз получить награду через <t:{int((last_reward_date + reward_delay).timestamp())}:R>")


class YouGotRewardEmbed(SuccessEmbed):
    def __init__(self, amount: str, reward_delay: timedelta):
        super().__init__(description=f"Вы получили награду: {amount} монет. Вы сможете ещё раз получить награду через <t:{int((datetime.today() + reward_delay).timestamp())}:R>")


class BalTopEmbed(InfoEmbed):
    def __init__(self, baltop: list[User]):
        super().__init__(description="Топ баланса:")
        for [place, user] in enumerate(baltop):
            match place:
                case 1:
                    place = ":first_place:"
                case 2:
                    place = ":second_place"
                case 3:
                    place = ":third_place"
            self.add_field(f"{place}.", f"<@{user.id}>\n{user.balance} монет", inline=False)


class YouSuccessfullyAwardedMoneyEmbed(SuccessEmbed):
    def __init__(self, amount: int, to: Member):
        super().__init__(description=f"Вы успешно выдали {amount} монет участнику {to.mention}.")
