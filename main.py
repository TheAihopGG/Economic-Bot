from disnake.ext import commands
from disnake import Intents
from bot.core.logger import logger

from bot.core.configuration import BOT_TOKEN
from bot.cogs.economic.cog import EconomicCog
from bot.cogs.help.cog import HelpCog
from bot.cogs.guild_settings.cog import GuildSettingsCog
from bot.cogs.shop.cog import ShopCog
from bot.cogs.promocode.cog import PromocodesCog

bot = commands.InteractionBot(intents=Intents.default())
[
    bot.add_cog(cog)
    for cog in {
        EconomicCog(),
        HelpCog(),
        GuildSettingsCog(),
        ShopCog(),
        PromocodesCog(),
    }
]


@bot.event
async def on_ready() -> None:
    logger.info("Bot ready")


bot.run(BOT_TOKEN)
