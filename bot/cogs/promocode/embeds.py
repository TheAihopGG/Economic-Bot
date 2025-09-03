from ...core.base_embeds import SuccessEmbed, ErrorEmbed, InfoEmbed
from ...core.models import Promocode


class PromocodesListEmbed(InfoEmbed):
    def __init__(
        self,
        promocodes: list[Promocode],
        show_full_info: bool,
    ):
        if promocodes:
            super().__init__(description="Список промокодов:")
            if show_full_info:
                for promocode in promocodes:
                    self.add_field(
                        name=promocode.code,
                        value=f"Выдаёт {promocode.bonus} монет\n \
                              {"Активен" if promocode.is_active else "Неактивен"}\
                              {(f"Допустимое количество использований: {promocode.max_usages}" if promocode.max_usages > 0 else "Использования промокода закончились")
                              if not promocode.is_infinite_usages else ""} \
                              {"Промокод ещё не использовали" if promocode.usages_count == 0 else f"Промокод использовали {promocode.usages_count} раз"}",
                    )
            else:
                for promocode in promocodes:
                    if promocode.is_infinite_usages or promocode.max_usages > promocode.usages_count:
                        self.add_field(
                            name=promocode.code,
                            value=f"Выдаёт {promocode.bonus} монет\n \
                                  {"Активен" if promocode.is_active else "Неактивен"}\
                                  {"Промокод ещё не использовали" if promocode.usages_count == 0 else f"Промокод использовали {promocode.usages_count} раз"}",
                        )
        else:
            super().__init__(description="На этом сервере ещё нет промокодов")


class YouAlreadyUsedPromocodeEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Вы уже использовали промокод")


class PromocodeWasNotFoundEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Промокод не найден")


class PromocodeIsNotActiveEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="Промокод уже не активен")


class PromocodeAlreadyHasMaximumUsagesCountEmbed(ErrorEmbed):
    def __init__(self):
        super().__init__(description="У промокода уже максимально допустимое количество использований")


class YouSuccessfullyUsedPromocodeEmbed(SuccessEmbed):
    def __init__(self, bonus: int):
        super().__init__(description=f"Вы успешно использовали промокод, получив {bonus} монет")
