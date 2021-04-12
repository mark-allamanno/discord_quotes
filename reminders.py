from discord.ext import commands
import discord

import dotenv

import os
import sys
import time
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

# Create a new bot with the prefix of '$' for commands
BOT = commands.Bot(command_prefix='$')

# Load the environment variables from the .env file and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RESOURCES_PATH = os.getenv('RESOURCE_FOLDER')


async def break_reminder(channel):
    """A function to send a 'Babe its time' meme in the chat to tell people to take their scheduled break from
    STEM homework and actually live a little"""

    # Get the image, font, and a surface to render the text to so we can write text on the image
    image = Image.open(Path(RESOURCES_PATH, 'babe-its-time.png'))
    font = ImageFont.truetype(str(Path(RESOURCES_PATH, 'dejavu.ttf')), 40)
    render = ImageDraw.Draw(image)

    # Write the meme text to the template with the current time, which is the request and yes honey response
    render.text((25, 650),
                f"Babe! It's {time.strftime('%I:%M%p')} time\n"
                f"for you to take a break",
                fill=(0, 0, 0),
                font=font)

    render.text((700, 575), 'Yes honey', fill=(0, 0, 0), font=font)

    # Then save the edited image, send it in chat with a message and then delete it from the filesystem
    image.save('reminder.png')
    await channel.send('@everyone Stop it, get some help', file=discord.File('reminder.png'))
    Path('reminder.png').unlink()


@BOT.event
async def on_ready() -> None:

    if 1 < len(sys.argv):  # Make sure we were given a reminder type to send

        # Get the correct server for this command to be sent in and then get the correct channel in th server as well
        server = discord.utils.find(lambda s: s.name == 'STEM Rehab', BOT.guilds)
        channel = discord.utils.find(lambda c: c.name == 'general', server.channels)

        if 'Break' == sys.argv[1]:
            await break_reminder(channel)

        elif 'Checkin' == sys.argv[1]:
            pass

        else:
            # Then send in the chat telling people to engage in the activity
            await channel.send('@everyone Its that time of day again, please post the best part about your day in the '
                               'chat. This is pseudo-mandatory meaning I cannot enforce it but you really should '
                               'or else your peers will be annoyed with you. Have a good night :) ')

    await BOT.close()  # Then shut the bot down as that is all we need it to do, runs via crontab at 11pm daily


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
