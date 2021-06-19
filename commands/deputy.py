import discord

import asyncio
import random
from pathlib import Path

from commands import *


@BOT.command(name='parole', brief='Forces a release of all prisoners in uwu jail if anyone abuses it or a malfunction '
                                  'occurs in the raspberry pi')
async def release_prisoners(ctx) -> None:
    """
    Prematurely removes people from the jail channel in case of a malfunction or an abuse of the system. This is
    done by typing in the command $parole and then mentioning every user you want to remove from the jail. Can only
    be used by me since not everyone in the server is trustworthy with such a power

    Parameters:
        ctx - The context from which this command was send

    Returns:
        Nothing
    """

    if ctx.message.author.name != 'Inquisitive Pikachu':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    inmate_role = discord.utils.find(lambda r: r.name == 'uwu-jail', ctx.guild.roles)
    inmate_channel = discord.utils.find(lambda c: c.name == 'uwu-jail', ctx.guild.channels)
    user_mentions = ', '.join([user.mention for user in ctx.message.mentions])

    await inmate_channel.send(f"{user_mentions} you're being let out early for good behavior. Dont make me regret it")
    await asyncio.sleep(3)

    for user in ctx.message.mentions:
        await user.remove_roles(inmate_role)

    await inmate_channel.purge()


@BOT.command(name='arrest', brief='Sends the mentioned users to the uwu jail for 5 minutes and then auto releases them')
async def detain_prisoners(ctx) -> None:
    """
    Moves the mentioned people into the restricted group for 5 minutes and then automatically let them out if
    everything goes as planned. You must type in $arrest and then mention all users you want to send to the jail
    channel for this to work.

    Parameters:
        ctx - The context from which this command was send

    Returns:
        Nothing
    """

    inmate_role = discord.utils.find(lambda r: r.name == 'uwu-jail', ctx.guild.roles)
    inmate_channel = discord.utils.find(lambda c: c.name == 'uwu-jail', ctx.guild.channels)
    user_mentions, screen_names = list(), list()

    for user in ctx.message.mentions:
        user_mentions.append(user.mention)
        screen_names.append(user.name)
        await user.add_roles(inmate_role)

    await ctx.channel.send(f'Users {", ".join(user_mentions)} have been sent to uwu jail for their crimes against '
                           f'humanity. You can rest easy now.')

    # Choose between the special and regular uwu jail pictures depending n if a specific person is in the jail
    # can also be sent randomly as an easter egg
    if 'TMI' in screen_names or .9 <= random.SystemRandom().random():
        image_file = discord.File(str(Path(RESOURCES_PATH, 'uwu-jail-baguette.jpg')))
    else:
        image_file = discord.File(str(Path(RESOURCES_PATH, 'uwu-jail.jpg')))

    await inmate_channel.send(file=image_file)
    await inmate_channel.send(f'{", ".join(user_mentions)} you are in uwu jail. You can leave when your uwu levels '
                              f'subside in approximately 5 minutes.')
    await asyncio.sleep(300)

    await inmate_channel.send(f"Your time is up inmate. Go back and be a productive member of the server.")
    await asyncio.sleep(3)

    for user in ctx.message.mentions:
        await user.remove_roles(inmate_role)

    await inmate_channel.purge()
