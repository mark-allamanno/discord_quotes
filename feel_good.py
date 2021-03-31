from discord.ext import commands
import discord

import dotenv

import os
import asyncio


# Create a new bot with the prefix of '$' for commands
BOT = commands.Bot(command_prefix='$')

# Load the environment variables from the .env file and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


@BOT.event
async def on_ready() -> None:
    """When the client connects to the discord server get the right channel and send the reminder before exiting"""

    # Get the correct server for this command to be sent in and then get the correct channel in th server as well
    server = discord.utils.find(lambda s: s.name == 'Test Server', BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'feel-good', server.channels)

    # Then send in the chat telling people to engage in the activity
    await channel.send(f'@everyone Its that time of day again, please post the best part about your day in the chat. '
                       f'This is pseudo-mandatory meaning I cannot enforce it but you really should or else your peers '
                       f'will be annoyed with you. Have a good night :)')

    # Stop the async event loop and exit the program
    asyncio.get_event_loop().stop()
    exit(0)


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
