import os
import dotenv
from discord.ext import commands


# Create a new bot with the prefix of '$' for commands
BOT = commands.Bot(command_prefix='$')

# Load the environment variables from the .env file and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Get the database and memes folder directories from the .env file
CSV_FILE = os.getenv('DATABASE_PATH')
MEMES_PATH = os.getenv('MEMES_FOLDER')
RESOURCES_PATH = os.getenv('RESOURCE_FOLDER')

# Get the channel that we are locking the bot to
CHANNEL_LOCK = os.getenv('CHANNEL_LOCK')

# Get the filename of the leaderboard image to send in the chat
TEMP_FILE_NAME = os.getenv('LEADERBOARD_NAME')


def lock_to_channel(channel):
    """Short decorator function to lock these commands to the channel we decide - present in the .env file"""
    return commands.check(lambda ctx: ctx.channel.name == channel)


def start_bot():
    """Short function to import all of the commands packages to add the commands to the bot then run the bot"""
    from . import deputy, leaderboard, memes, miscellaneous, quotes
    BOT.run(TOKEN)
