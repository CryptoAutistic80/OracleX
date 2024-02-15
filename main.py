# ________  ________      ___    ___ ________  _________  ________          ________  ___  ___  _________  ___  ________  _________  ___  ________
#|\   ____\|\   __  \    |\  \  /  /|\   __  \|\___   ___\\   __  \        |\   __  \|\  \|\  \|\___   ___\\  \|\   ____\|\___   ___\\  \|\   ____\
#\ \  \___|\ \  \|\  \   \ \  \/  / | \  \|\  \|___ \  \_\ \  \|\  \       \ \  \|\  \ \  \\\  \|___ \  \_\ \  \ \  \___|\|___ \  \_\ \  \ \  \___|
# \ \  \    \ \   _  _\   \ \    / / \ \   ____\   \ \  \ \ \  \\\  \       \ \   __  \ \  \\\  \   \ \  \ \ \  \ \_____  \   \ \  \ \ \  \ \  \
#  \ \  \____\ \  \\  \|   \/  /  /   \ \  \___|    \ \  \ \ \  \\\  \       \ \  \ \  \ \  \\\  \   \ \  \ \ \  \|____|\  \   \ \  \ \ \  \ \  \____
#   \ \_______\ \__\\ _\ __/  / /      \ \__\        \ \__\ \ \_______\       \ \__\ \__\ \_______\   \ \__\ \ \__\____\_\  \   \ \__\ \ \__\ \_______\
#    \|_______|\|__|\|__|\___/ /        \|__|         \|__|  \|_______|        \|__|\|__|\|_______|    \|__|  \|__|\_________\   \|__|  \|__|\|_______|
#                      \|___|/                                                                                   \|_________|

#          ___  _____ ______   ________  ________  ___  ________   _______   _______   ________
#         |\  \|\   _ \  _   \|\   __  \|\   ____\|\  \|\   ___  \|\  ___ \ |\  ___ \ |\   __  \
#         \ \  \ \  \\\__\ \  \ \  \|\  \ \  \___|\ \  \ \  \\ \  \ \   __/|\ \   __/|\ \  \|\  \
#          \ \  \ \  \\|__| \  \ \   __  \ \  \  __\ \  \ \  \\ \  \ \  \_|/_\ \  \_|/_\ \   _  _\
#           \ \  \ \  \    \ \  \ \  \ \  \ \  \|\  \ \  \ \  \\ \  \ \  \_|\ \ \  \_|\ \ \  \\  \|
#            \ \__\ \__\    \ \__\ \__\ \__\ \_______\ \__\ \__\\ \__\ \_______\ \_______\ \__\\ _\
#             \|__|\|__|     \|__|\|__|\|__|\|_______|\|__|\|__| \|__|\|_______|\|_______|\|__|\|__|
#
# SShift DAO - 2024
# http://www.sshift.xyz
#
import logging
import logging.handlers
import os

import nextcord
from nextcord.ext import commands

# Update the import statement to include the new function name
from database.database import create_or_update_guild_membership, create_tables
from server import keep_alive


def setup_logging():
    """Configure logging for the bot."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(filename='discord.log', encoding='utf-8', maxBytes=10**7, backupCount=1)
    console_handler = logging.StreamHandler()

    fmt = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

def load_cogs(bot, logger):
    """Load all cogs from the cogs directory."""
    cogs_directory = "cogs"
    for filename in os.listdir(cogs_directory):
        if filename.endswith(".py"):
            cog_path = f"{cogs_directory}.{filename[:-3]}"
            try:
                bot.load_extension(cog_path)
                logger.info(f"Loaded cog: {cog_path}")
            except Exception as e:
                logger.error(f"Failed to load cog: {cog_path}. Error: {e}")

logger = setup_logging()

intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name}!')
    await create_tables()
    logger.info('Database tables initialized.')

@bot.event
async def on_guild_join(guild):
    # Assume a default membership type on guild join; adjust as necessary
    await create_or_update_guild_membership(guild.id, 'FREE')
    logger.info(f"Guild membership created or updated for: {guild.name} (ID: {guild.id})")

load_cogs(bot, logger)

keep_alive()

bot.run(os.getenv('DISCORD_TOKEN'))