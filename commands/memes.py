import discord

import random
from pathlib import Path

from commands import *


SEEN_MEMES = set()  # A global variable that keeps track of all 'stale' memes


@BOT.command(name='add-meme', brief='Adds a new meme to the database associated with a specific person')
@lock_to_channel(CHANNEL_LOCK)
async def save_meme(ctx, author: str, *filenames) -> None:
    """
    A command to save pictures to the database, which we call memes. It will save this meme into the specified
    authors directory, and save it under the filename you give it, and can take in a variable number of attachments
    and filenames. Simply add an image with a command of the form $add-meme author filename1 filename2 and so one
    with one filename per image.

    Parameters:
        ctx - The context from which this command was send
        author - A string of the user for which we want to associate these memes with
        *filenames - The variable list of filenames to save each attachment as

    Returns:
        Nothing

    """

    author = author.lower() # Lowercase the input author for homogeneity

    if not Path(MEMES_PATH, author).exists():
        Path(MEMES_PATH, author).mkdir()

    for attachment, file in zip(ctx.message.attachments, filenames):

        filename = f'{file.lower()}{Path(attachment.filename).suffix}'
        present_files = [name.stem for name in Path(MEMES_PATH, author).iterdir()]

        if filename not in present_files:
            await attachment.save(str(Path(MEMES_PATH, author, filename)))
        else:
            await ctx.channel.send(f'Filename, {filename}, for user {author} is already taken, try again!')

    await ctx.channel.send('Meme has been saved to the database for future usage.')


@BOT.command(name='delete-meme', brief='Removes a mistyped or mis-associated meme from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_meme(ctx, author=None, filename=None) -> None:
    """
    Removes a specified meme from the database in the case of a typo or duplicate. To use you must type in the
    command $delete-meme and then specify an author to remove a meme from and then the filename of the meme you
    would like to remove, that means something like $delete-meme author filename. THis is a privileged action so
    only the admins can use it.

    Parameters:
        ctx - The context from which this command was send
        author - The author for which we want to remove a meme from
        filename - the filename of hte meme to remove from their directory

    Returns:
        Nothing
    """

    author = author.lower()  # Lowercase the input author for homogeneity

    if ctx.message.author.name != 'Bob the Great':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    elif not Path(MEMES_PATH, author).exists():
        await ctx.channel.send(f"{author} doesn't exist in the database, so we cannot remove a meme for them.")
        return

    elif author is None or filename is None:
        await ctx.channel.send("Query cannot be completed because you did not give enough information.")
        return

    for meme_file in Path(MEMES_PATH, author).iterdir():

        if meme_file.stem == filename:
            meme_file.unlink()
            await ctx.channel.send(f"Meme {meme_file.name} was remove from {author}'s meme folder successfully")
            return

    await ctx.channel.send(f"Meme was not present in {author}'s directory, are you sure this is the right name?")


@BOT.command(name='meme', brief='Sends back a meme associated with a specified person or anyone if left unfilled')
@lock_to_channel(CHANNEL_LOCK)
async def get_meme(ctx, author='random', requested_meme=None) -> None:
    """
    Send back a meme that is associated with a given author if they exist in the database, if they do not exist then
    throw an error. This one is basically the same thing as the $quote command, nothing special. Just type in $meme
    author to send back a meme relating to that author, or just $meme to send back someone random.

    Parameters:
        ctx - The context from which this command was send
        author - The author for which we want to get a random meme of

    Returns:
        Nothing
    """

    global SEEN_MEMES        # Make sure we can edit the global set if applicable
    author = author.lower()  # Make sure the author's name is lowercase for homogeneity

    if not Path(MEMES_PATH, author).exists() and author != 'random':
        await ctx.channel.send(f'{author} has no memes associated with them. Add some!')
        return

    elif requested_meme is not None:

        if not Path(MEMES_PATH, author, requested_meme).exists():
            await ctx.channel.send(f"This meme does not exist in the database, are you sure you're using this right?")
        elif author == 'random':
            await ctx.channel.send(f"Cannot request a specified meme for any author, that's illegal")
        else:
            await ctx.channel.send(file=discord.File(str(Path(MEMES_PATH, author, requested_meme))))

        return

    random_gen = random.SystemRandom()

    if author == 'random':
        author = random_gen.choice(list(Path(MEMES_PATH).iterdir()))

    all_memes = {str(file) for file in Path(MEMES_PATH, author).iterdir()}
    remove_duplicates = all_memes - SEEN_MEMES

    if not remove_duplicates:
        SEEN_MEMES -= all_memes
        meme = random_gen.choice(list(all_memes))
    else:
        meme = random_gen.choice(list(remove_duplicates))

    SEEN_MEMES.add(str(meme))
    await ctx.channel.send(file=discord.File(str(Path(MEMES_PATH, author, meme))))


@BOT.command(name='list-memes', brief='Sends back a meme associated with a specified person or anyone if left unfilled')
@lock_to_channel(CHANNEL_LOCK)
async def list_memes(ctx, author=None):

    if author is None:
        await ctx.channel.send(f"No author was specified to list the associated memes for!")
        return

    elif not Path(MEMES_PATH, author).exists():
        await ctx.channel.send(f"This author does not exist in the database, so they have no memes!")
        return

    all_meme_names = '\n'.join(sorted([meme.name for meme in Path(MEMES_PATH, author).iterdir()]))
    await ctx.channel.send(f"All memes associated with the author are as follows:\n{all_meme_names}")
