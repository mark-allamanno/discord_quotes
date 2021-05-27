from pathlib import Path

import discord

from commands import *


@BOT.command(name='summon-him', brief='Summons Picklechu from the void')
@lock_to_channel(CHANNEL_LOCK)
async def summon_picklechu(ctx) -> None:
    """Sends a picture of Picklechu in chat so everyone can know true fear"""
    await ctx.channel.send(file=discord.File(str(Path(RESOURCES_PATH, 'picklechu.png'))))


@BOT.event
async def on_ready() -> None:
    """When the client connects to the discord server print out a confirmation message and change presence"""

    print(f'Connected to Discord Successfully!')

    await BOT.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name='Tingledorf')
    )


@BOT.command(name='change-reminders', brief='Changes the name of the server to send the reminders to')
async def change_reminder_server(ctx, server_name):
    dotenv.set_key('/home/pi/.env', 'REMINDER', server_name)
    await ctx.channel.send(f"Group reminders will now be send to the server {server_name}")
