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

    # Make sure it was me that sent the parole request, otherwise lock them out
    if ctx.message.author.name != 'Inquisitive Pikachu':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    # Get the inmate channel and role so we can send a message and then release the prisoners
    inmate_role = discord.utils.find(lambda r: r.name == 'uwu-jail', ctx.guild.roles)
    inmate_channel = discord.utils.find(lambda c: c.name == 'uwu-jail', ctx.guild.channels)
    user_mentions = ', '.join([user.mention for user in ctx.message.mentions])

    # Send the prisoners a message that they are being saved and wait a second for them to read it
    await inmate_channel.send(f"{user_mentions} you're being let out early for good behavior. Dont make me regret it")
    await asyncio.sleep(3)

    # Iterate over all users of the server and remove their uwu jail role if they have it
    for user in ctx.message.mentions:
        await user.remove_roles(inmate_role)

    # Finally purge the uwu jail channel so that next time it will be like the first time
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

    # Get the role and the channel of the uwu jail in the current server
    inmate_role = discord.utils.find(lambda r: r.name == 'uwu-jail', ctx.guild.roles)
    inmate_channel = discord.utils.find(lambda c: c.name == 'uwu-jail', ctx.guild.channels)
    user_mentions, screen_names = list(), list()

    for user in ctx.message.mentions:
        # Add each detained user's mention and their screen name
        user_mentions.append(user.mention)
        screen_names.append(user.name)

        # Then send them to the jail role where they are locked from speaking for 5 minutes
        await user.add_roles(inmate_role)

    # Let the invoking channel know what has happened to the user since they wont be visible for while
    await ctx.channel.send(f'Users {", ".join(user_mentions)} have been sent to uwu jail for their crimes against '
                           f'humanity. You can rest easy now.')

    # Choose between the special and regular uwu jail pictures depending n if a specific person is in the jail
    # can also be sent randomly as an easter egg
    if 'TMI' in screen_names or .9 <= random.SystemRandom().random():
        image_file = discord.File(str(Path(RESOURCES_PATH, 'uwu-jail-baguette.jpg')))
    else:
        image_file = discord.File(str(Path(RESOURCES_PATH, 'uwu-jail.jpg')))

    # Then send them the uwu jail bonk picture and let then know that they are locked out. Finally sleep the thread
    # for 5 minutes and then release them in much the same way
    await inmate_channel.send(file=image_file)
    await inmate_channel.send(f'{user_mentions} you are in uwu jail. You can leave when your uwu levels '
                              f'subside in approximately 5 minutes.')
    await asyncio.sleep(300)

    # After we have waited the requisite amount of time then send them a message letting them know they are being freed
    await inmate_channel.send(f"Your time is up inmate. Go back and be a productive member of the server.")
    await asyncio.sleep(3)

    # Free then from the jail that they were locked to for the time duration
    for user in ctx.message.mentions:
        await user.remove_roles(inmate_role)

    # Finally purge the uwu jail channel so that next time it will be like the first time
    await inmate_channel.purge()
