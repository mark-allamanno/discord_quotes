import asyncio
import os
import random
import sys
import time
from pathlib import Path

import discord
import dotenv
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands


BOT = commands.Bot(command_prefix='$')

dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RESOURCES_PATH = os.getenv('RESOURCE_FOLDER')
REMINDER_SERVER = os.getenv('REMINDER')


async def break_reminder(channel):
    """A function to send a 'Babe its Time' meme in the chat to tell people to take their scheduled break from
    STEM homework and actually live a little"""

    image = Image.open(Path(RESOURCES_PATH, 'babe-its-time.png'))
    font = ImageFont.truetype(str(Path(RESOURCES_PATH, 'dejavu.ttf')), 40)
    render = ImageDraw.Draw(image)

    render.text((25, 650), f"Babe! It's {time.strftime('%I:%M%p')}, time\nfor you to take a break",
                fill=(0, 0, 0), font=font)
    render.text((700, 575), 'Yes honey', fill=(0, 0, 0), font=font)

    image.save('reminder.png')
    await channel.send('@everyone Stop it, get some help', file=discord.File('reminder.png'))
    Path('reminder.png').unlink()


@BOT.event
async def on_ready() -> None:

    if 1 < len(sys.argv):

        channel_name = 'general' if sys.argv[1] != 'Checkin' else 'reminders'
        server = discord.utils.find(lambda s: s.name == REMINDER_SERVER, BOT.guilds)
        channel = discord.utils.find(lambda c: c.name == channel_name, server.channels)

        if 'Break' == sys.argv[1]:
            await break_reminder(channel)
        elif 'Checkin' == sys.argv[1]:
            await asyncio.sleep(random.SystemRandom().randint(10, 55) * 60)
            await channel.send("@everyone Go check in and make sure she's actually taking her break.")
        else:
            await channel.send("@everyone It's that time of day again, please send the best part of your day in chat "
                               "so we can all feel a little better :)")

    await BOT.close()


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
