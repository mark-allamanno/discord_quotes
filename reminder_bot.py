import asyncio
import os
import random
import time
import argparse
from pathlib import Path

import discord
import dotenv
from PIL import Image, ImageFont, ImageDraw
from discord.ext import commands


INTENTS = discord.Intents.default()
INTENTS.members = True
BOT = commands.Bot(command_prefix='$', intents=INTENTS)

dotenv.load_dotenv()
TOKEN = os.getenv('REMINDER_TOKEN')
RESOURCES_PATH = os.getenv('RESOURCE_FOLDER')
FUN_REMINDER_SERVER = os.getenv('FUN_REMINDERS')
REQUIRED_REMINDER_SERVER = os.getenv('REQ_REMINDERS')


async def checkin_reminder():
    server = discord.utils.find(lambda s: s.name == FUN_REMINDER_SERVER, BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'reminders', server.channels)

    await asyncio.sleep(random.SystemRandom().randint(10, 55) * 60)
    await channel.send("@everyone Go check in and make sure she's actually taking her break.")


async def feel_good_reminder():
    server = discord.utils.find(lambda s: s.name == FUN_REMINDER_SERVER, BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'general', server.channels)

    await channel.send("@everyone It's that time of day again, please send the best part of your day in chat "
                       "so we can all feel a little better :)")


async def break_reminder():
    """A function to send a 'Babe its Time' meme in the chat to tell people to take their scheduled break from
    STEM homework and actually live a little"""

    server = discord.utils.find(lambda s: s.name == FUN_REMINDER_SERVER, BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'general', server.channels)

    image = Image.open(Path(RESOURCES_PATH, 'babe-its-time.png'))
    font = ImageFont.truetype(str(Path(RESOURCES_PATH, 'dejavu.ttf')), 40)
    render = ImageDraw.Draw(image)

    render.text((25, 650), f"Babe! It's {time.strftime('%I:%M%p')}, time\nfor you to take a break",
                fill=(0, 0, 0), font=font)
    render.text((700, 575), 'Yes honey', fill=(0, 0, 0), font=font)

    image.save('reminder.png')
    await channel.send('@everyone Stop it, get some help', file=discord.File('reminder.png'))
    Path('reminder.png').unlink()


async def send_rent_money_reminder():
    server = discord.utils.find(lambda s: s.name == REQUIRED_REMINDER_SERVER, BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'general', server.channels)

    await channel.send("@everyone It's that time of the month again, please aggregate our rent money and sent it to "
                       "the landlord before we get evicted.")


async def check_rent_money_sent():

    server = discord.utils.find(lambda s: s.name == REQUIRED_REMINDER_SERVER, BOT.guilds)
    channel = discord.utils.find(lambda c: c.name == 'general', server.channels)

    bot_reminder_message = await channel.history().find(
        lambda m: m.content == "@everyone It's that time of the month again, please aggregate our rent money and sent "
                               "it to the landlord before we get evicted.")

    all_reacted_users = set()

    for reaction in bot_reminder_message.reactions:
        emoji_reactions = await reaction.users().flatten()
        all_reacted_users |= set(emoji_reactions)

    users_to_callout = [user.mention for user in server.members if user not in all_reacted_users and not user.bot]

    if users_to_callout:
        await channel.send(f"{' '.join(users_to_callout)} send your dang rent money fools! This is your last warning.")
    else:
        await channel.send(f"@everyone Nice we wont get evicted for another month! Thanks everyone :partying_face:")


def parse_command_line_args():

    parser = argparse.ArgumentParser("Command Line Tool to periodically send reminder messages in our fiend group's "
                                     "Discord server")

    parser.add_argument('-c', '--checkin-reminder', action='store_true')
    parser.add_argument('-f', '--feel-good-reminder', action='store_true')
    parser.add_argument('-b', '--break-reminder', action='store_true')
    parser.add_argument('-s', '--send-rent-money-reminder', action='store_true')
    parser.add_argument('-m', '--check-money-sent-reminder', action='store_true')
    parser.add_argument('-d', '--run-as-daemon', action='store_true')

    return parser.parse_args()


async def auxiliary_setup():

    print(f'Connected to Discord Successfully!')

    await BOT.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="Everyone's Souls")
    )


@BOT.event
async def on_ready() -> None:

    command_line_args = parse_command_line_args()
    await auxiliary_setup()

    if command_line_args.checkin_reminder:
        await checkin_reminder()

    if command_line_args.feel_good_reminder:
        await feel_good_reminder()

    if command_line_args.break_reminder:
        await break_reminder()

    if command_line_args.send_rent_money_reminder:
        await send_rent_money_reminder()

    if command_line_args.check_money_sent_reminder:
        await check_rent_money_sent()

    if not command_line_args.run_as_daemon:
        await BOT.close()


if __name__ == '__main__':
    BOT.run(TOKEN)  # Application entry point
