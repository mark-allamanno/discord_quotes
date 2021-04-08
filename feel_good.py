from discord.ext import commands
import discord

import dotenv

import os
import sys

# Create a new bot with the prefix of '$' for commands
BOT = commands.Bot(command_prefix='$')

# Load the environment variables from the .env file and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


@BOT.event
async def on_ready() -> None:
    """When the client connects to the discord server get the right channel and send the reminder before exiting"""

    # Get the correct server for this command to be sent in and then get the correct channel in th server as well
    server = discord.utils.find(lambda s: s.name == 'STEM Rehab', BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'feel-good', server.channels)

    if 1 < len(sys.argv) and sys.argv[1] == 'Break Reminder':
        message = "Its that time of day again, please begin your regularly scheduled break. Also post what you plan " \
                  "to do with this break in chat so we can validate you are actually doing it. Also please do your " \
                  "best to enjoy it :) "
    else:
        message = "Its that time of day again, please post the best part about your day in the chat. This is " \
                  "pseudo-mandatory meaning I cannot enforce it but you really should or else your peers will be " \
                  "annoyed with you. Have a good night :) "

    # Then send in the chat telling people to engage in the activity
    await channel.send(f'@everyone {message}')

    await BOT.close()  # Then shut the bot down as that is all we need it to do, runs via crontab at 11pm daily


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
