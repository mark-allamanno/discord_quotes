import discord

from pathlib import Path

from commands import *


@BOT.command(name='summon-him', brief='Summons Picklechu from the void')
@lock_to_channel(CHANNEL_LOCK)
async def summon_picklechu(ctx) -> None:
    """Sends a picture of Picklechu in chat so everyone can know true fear"""
    await ctx.channel.send(file=discord.File(str(Path(RESOURCES_PATH, 'picklechu.png'))))
