from disnake.ext import commands
from disnake import Intents
from bot.core.logger import logger

from bot.core.configuration import BOT_TOKEN
from bot.cogs.economic.cog import EconomicCog
from bot.cogs.help.cog import HelpCog
from bot.cogs.guild_settings.cog import GuildSettingsCog

bot = commands.InteractionBot(intents=Intents.default())
[
    bot.add_cog(cog)
    for cog in {
        EconomicCog(),
        HelpCog(),
        GuildSettingsCog(),
    }
]


@bot.event
async def on_ready() -> None:
    logger.info("Bot ready")


bot.run(BOT_TOKEN)
