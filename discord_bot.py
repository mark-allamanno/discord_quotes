import discord

from commands import *
from commands import leaderboard, memes, miscellaneous, prison, quotes


@BOT.event
async def on_ready() -> None:
    """When the client connects to the discord server print out a confirmation message and change presence"""

    print(f'Connected to Discord Successfully!')

    await BOT.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name='Tingledorf')
    )


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
