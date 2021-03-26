from discord.ext import commands
import discord

import dotenv

import matplotlib.pyplot as plt

import numpy as np

import os
import csv
import random
import asyncio
from pathlib import Path
from collections import defaultdict
from heapq import nlargest
from typing import Dict, List, Tuple


# Create a new bot with the prefix of '$' for commands
BOT = commands.Bot(command_prefix='$')

# Load the environment variables from the .env file and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Get the database and memes folder directories from the .env file
CSV_FILE = os.getenv('DATABASE_PATH')
MEMES_PATH = os.getenv('MEMES_FOLDER')

# Get the channel that we are locking the bot to
CHANNEL_LOCK = os.getenv('CHANNEL_LOCK')

# Get the filename of the leaderboard image to send in the chat
TEMP_FILE_NAME = os.getenv('LEADERBOARD_NAME')

# Then finally declare a set of seen quotes and memes at this point in time to force new random things
SEEN_QUOTES = set()
SEEN_MEMES = set()


def lock_to_channel(channel) -> bool:
    """Short decorator function to lock these commands to the channel we decide - present in the .env file"""
    return commands.check(lambda ctx: ctx.channel.name == channel)


def all_quotes_by(author) -> List[Tuple[str]]:
    """Get all the quotes by a specified person. Returns a list of lists of a person's quotes"""

    global SEEN_QUOTES  # Use the global seen quotes variable

    with open(CSV_FILE, 'r') as college_quotes:

        all_quotes = set()  # Create a new set of all he quotes that involve this person

        # Get all of the quotes of the specific person and remove any duplicate quotes
        for quote in csv.reader(college_quotes):
            if author == 'random' or any(author.title() in quote[i] for i in range(1, len(quote), 2)):
                all_quotes.add(tuple(quote))

        remove_duplicates = all_quotes - SEEN_QUOTES

        # If every quote of theirs has already been sent then remove them from seen and return all their quotes
        if not remove_duplicates:
            SEEN_QUOTES -= all_quotes
            return list(all_quotes)

        # Otherwise just return the new and fresh quotes
        return list(remove_duplicates)


def get_statistics_dict() -> Dict[str, Tuple[int, int]]:
    """Get the total count of each person's quotes and memes in the database as a dictionary of the form
    Name -> (# Quotes, # Memes)"""

    # Declare default dictionary of peoples names to their quote/meme counts
    scoreboard = defaultdict(lambda: (0, 0))

    # Open the csv file of all of the quotes inside of it
    with open(CSV_FILE, 'r') as college_quotes:

        # Get every component of every line in the csv file as we need to check each line for its authors
        for quote in csv.reader(college_quotes):
            for index, author in enumerate(quote):

                if index % 2 == 1:
                    quotes, memes = scoreboard[author]
                    scoreboard[author] = quotes + 1, memes

    # Iterate over all the meme folders and update each authors count with the number of memes in their folder
    for author in Path(MEMES_PATH).iterdir():
        quotes, memes = scoreboard[author.stem.title()]
        scoreboard[author.stem.title()] = quotes, len(list(author.iterdir()))

    return scoreboard


@BOT.command(name='parole', brief='Forces a release of all prisoners in uwu jail if anyone abuses it')
async def release_prisoners(ctx) -> None:
    """Prematurely removes people from the jail in case of a malfunction or an abuse of the system"""

    # Make sure it was me that sent the parole request, otherwise lock them out
    if ctx.message.author.name != 'Deadpool':
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


@BOT.command(name='arrest', brief='Sends the mentioned users to the uwu jail for 5 minutes')
async def detain_prisoners(ctx) -> None:
    """Moves specified people into the restricted group for 10 minutes and then automatically let them out"""

    # Get the role and the channel of the uwu jail in the current server along with all mentions for the users
    inmate_role = discord.utils.find(lambda r: r.name == 'uwu-jail', ctx.guild.roles)
    inmate_channel = discord.utils.find(lambda c: c.name == 'uwu-jail', ctx.guild.channels)
    user_mentions = ', '.join([user.mention for user in ctx.message.mentions])

    # Then add all mentioned users to the uwu jail so they are locked there
    for user in ctx.message.mentions:
        await user.add_roles(inmate_role)

    # Let the invoking channel know what has happened to the user since they wont be visible for while
    await ctx.channel.send(f'Users {user_mentions} have been sent to uwu jail for their crimes against humanity. '
                           f'You can rest easy now.')

    # Then send them the uwu jail bonk picture and let then know that they are locked out. Finally sleep the thread
    await inmate_channel.send(file=discord.File(str(Path(MEMES_PATH, 'general', 'uwu-jail.jpg'))))
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


@BOT.command(name='summon-him', brief='Summons Picklechu from the void')
@lock_to_channel(CHANNEL_LOCK)
async def summon_picklechu(ctx) -> None:
    """Sends a picture of Picklechu in chat so everyone can know fear"""
    await ctx.channel.send(file=discord.File(str(Path(MEMES_PATH, 'general', 'picklechu.png'))))


@BOT.command(name='add-quote', brief='Command to add a new quote to the database')
@lock_to_channel(CHANNEL_LOCK)
async def save_quote(ctx, *quote) -> None:
    """Adds a specified quote to the CSV file. Can take in a variable amount of quote/author pairs"""

    # Make sure the length of the arguments parameter makes sense before attempting to add it
    if len(quote) % 2 == 1:
        await ctx.channel.send('Malformed query, the quote should be in the form "quote" author "quote" author...')
        return

    with open(CSV_FILE, 'r') as college_quotes:

        # Iterate over all rows of the csv file and make sure that this quote does not match it exactly
        for row in csv.reader(college_quotes):
            if all([string.lower() == partial.lower() for string, partial in zip(row, quote)]):
                await ctx.channel.send('This quote already exists in the database, no need to add it again.')
                return

    with open(CSV_FILE, 'a') as college_quotes:

        # Open a new CSV writer and then write the quote surrounded by quotation marks to the college_quotes.csv file
        writer = csv.writer(college_quotes, quoting=csv.QUOTE_ALL)
        writer.writerow([s.title() if i % 2 else s for i, s in enumerate(quote)])

        # Then send a confirmation message so the user knows it was added
        await ctx.channel.send('Successfully added quote to database for future usage')


@BOT.command(name='delete-quote', brief='Command to remove a mistyped quote from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_quote(ctx, *args) -> None:
    """Removes a specified quote from the database in the case of a typo or duplicate"""

    # Make sure the user that we want is making these edits to the database
    if ctx.message.author.name != 'Bob the Great':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    # If the user didnt input any arguments or they input an odd number of arguments then the query is strange,
    # so dont parse it
    if len(args) == 0 or len(args) % 2 == 1:
        await ctx.channel.send("You either didn't give a quote to delete or the quote's formatted was malformed.")
        return

    partial_quote = list(args)  # Convert the arguments to a list so we can check for sublist

    with open(CSV_FILE, 'r') as quotes_read, open('college-quotes-edited.csv', 'w') as quotes_write:

        # Open a new CSV writer and create a boolean to track the removed quote
        csv_writer = csv.writer(quotes_write, quoting=csv.QUOTE_ALL)
        quote_removed = False

        # Read every line from the original csv file and only write it to the new one of it oes not match the quote to
        # remove given by the user
        for row in csv.reader(quotes_read):
            if not all([quote.lower() == partial.lower() for quote, partial in zip(row, partial_quote)]):
                csv_writer.writerow(row)
            else:
                quote_removed = True

    # Then finally remove the old file and rename the new file to take its place
    Path(CSV_FILE).unlink()
    Path('college-quotes-edited.csv').rename(CSV_FILE)

    # Confirm to the user that their actions have actually done something or let them know something went wrong
    if quote_removed:
        await ctx.channel.send("Quote successfully removed from the database!")
    else:
        await ctx.channel.send("Quote was not found in the database, are you sure it is correct?")


@BOT.command(name='quote', brief='Command to fetch a quote by a specified person or anyone if left unfilled.')
@lock_to_channel(CHANNEL_LOCK)
async def get_quote(ctx, quote_author='random') -> None:
    """Get a random quote by the person specified in the argument. Searched the database for quotes by them and
    returns sends a random one back as a response"""

    # Get all the quotes by a specific person and then choose how to handle it
    quotes_list = all_quotes_by(quote_author)

    if quotes_list:  # Make sure the requested author has quotes to search

        # Get a random quote from the list of quotes and parse them into quote, author pairs
        quote = random.SystemRandom().choice(quotes_list)
        quote_list = [(quote[i], quote[i + 1]) for i in range(0, len(quote), 2)]

        # Since we are now sending this quote add it to the seen quotes set
        SEEN_QUOTES.add(tuple(quote))

        # Iterate over all pairs and send them as a message to the server. This accounts for multi-quotes
        for quotation, author in quote_list:
            await ctx.channel.send(f'**"{quotation}"**\n'
                                   f'-*{author.title()}*')

    else:
        await ctx.channel.send(f'{quote_author} not found in the database. Add some quotes for them!')


@BOT.command(name='add-meme', brief='Command to add meme to the database associated with a specific person.')
@lock_to_channel(CHANNEL_LOCK)
async def save_meme(ctx, author, *filenames) -> None:
    """Saves memes with given filenames to the servers meme archive"""

    author = author.lower()  # Make sure the author's name is lowercase for homogeneity

    # If the path to the user doesnt exist then we need to create it to prevent issues later
    if not Path(MEMES_PATH, author).exists():
        Path(MEMES_PATH, author).mkdir()

    for attachment, file in zip(ctx.message.attachments, filenames):

        # Create a valid filename with extension for the file and get all filenames already present in the directory
        filename = f'{file.lower()}{Path(attachment.filename).suffix}'
        present_files = [name.stem for name in Path(MEMES_PATH, author).iterdir()]

        # Then upload the file only if it has a unique name otherwise let the user know it failed
        if filename not in present_files:
            await attachment.save(str(Path(MEMES_PATH, author, filename)))
        else:
            await ctx.channel.send(f'Filename, {filename}, for user {author} is already taken, try again!')

    # Then let the user know we have saved the meme successfully
    await ctx.channel.send('Meme has been saved to the database for future usage.')


@BOT.command(name='delete-meme', brief='Command to remove a mistyped or mis-associated meme from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_meme(ctx, author=None, filename=None) -> None:
    """Removes a specified meme from the database in the case of a typo or duplicate"""

    author = author.lower()  # Lowercase the input author for homogeneity

    # Make sure the user that we want is making these edits to the database
    if ctx.message.author.name != 'Bob the Great':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    # If the path to the given author does not exist then we cannot delete any memes for them
    if not Path(MEMES_PATH, author).exists():
        await ctx.channel.send(f"{author} doesn't exist in the database, so we cannot remove a meme for them.")
        return

    # Make sure the user gave us the correct amount of arguments or else fail out
    elif author is None or filename is None:
        await ctx.channel.send("Query cannot be completed because you did not give enough information.")
        return

    # Otherwise iterate over the given directory to find the file to delete and delete it
    for meme_file in Path(MEMES_PATH, author).iterdir():

        if meme_file.stem == filename:
            await ctx.channel.send(f"Meme {meme_file.name} was remove from {author}'s meme folder successfully")
            meme_file.unlink()
            return

    # If we make it here then we never found the file to remove, so something is wrong. Let the user know
    await ctx.channel.send(f"Meme was not present in {author}'s directory, are you sure this is the right name?")


@BOT.command(name='meme', brief='Command to send back a meme associated with a specified person.')
@lock_to_channel(CHANNEL_LOCK)
async def get_meme(ctx, author='random') -> None:
    """Send back a meme that is associated with a given author if they exist in the database"""

    global SEEN_MEMES  # Use the global seen memes variable
    author = author.lower()  # Make sure the author's name is lowercase for homogeneity

    # Then make sure the author exists in the database before pulling a meme
    if not Path(MEMES_PATH, author).exists() and author != 'random':
        await ctx.channel.send(f'{author} has no memes associated with them. Add some!')
        return

    # Create a new random generator to pick out our memes for us
    random_gen = random.SystemRandom()

    # Randomly choose a person if that is what the user asked for
    if author == 'random':
        author = random_gen.choice(list(Path(MEMES_PATH).iterdir()))

    # Then get all of the memes for this person and remove the duplicate from the possible pool
    all_memes = {str(file) for file in Path(MEMES_PATH, author).iterdir()}
    remove_duplicates = all_memes - SEEN_MEMES

    # If all of the memes are duplicates then remove all of their memes and choose from the total pool
    if not remove_duplicates:
        SEEN_MEMES -= all_memes
        meme = random_gen.choice(list(all_memes))
    else:
        meme = random_gen.choice(list(remove_duplicates))

    # Then add the newly chosen meme to the seen set and send it in chat
    SEEN_MEMES.add(str(meme))
    await ctx.channel.send(file=discord.File(str(Path(MEMES_PATH, author, meme))))


@BOT.command(name='leaderboard', brief='Command to see the overall number of memes/quotes associated with each person')
@lock_to_channel(CHANNEL_LOCK)
async def get_statistics(ctx, *args) -> None:
    """Send back a graph that represents the current number of quotes/memes for each person in the database"""

    scoreboard_info = get_statistics_dict()  # Get the scoreboard in the form Name -> (# Quotes, # Memes)

    # If there are no more arguments then just send the base leaderboard with everyone in it
    if len(args) == 0:
        await send_leaderboard_image(ctx, scoreboard_info)

    # If the user is requesting to see the leaderboard of only the top n people then send that instead
    elif len(args) == 1 and args[0].isdigit():
        await send_leaderboard_image(ctx, scoreboard_info, top_n_authors=int(args[0]))

    # Maybe they are trying to only see the leaderboard for a couple of people in which case only show those people
    elif all([name.title() in scoreboard_info for name in args]):
        await send_leaderboard_image(ctx, scoreboard_info, requested_authors=args)

    # Otherwise they messed something up so let them know
    else:
        await ctx.channel.send("Malformed leaderboard query, cannot complete request")


async def send_leaderboard_image(ctx, scoreboard, requested_authors=None, top_n_authors=0) -> None:
    """A relatively long function that parses the raw scoreboard data into a matplotlib graph and then sends that
    graph in the querying channel"""

    # If we only want the top n authors to be displayed then filter out all others before we start
    if top_n_authors:
        scoreboard = {x: scoreboard[x] for x in nlargest(top_n_authors, scoreboard, key=lambda x: sum(scoreboard[x]))}

    # If we only want to see the scoreboard for a handful of specific people then make sure all their names are lower
    if requested_authors:
        requested_authors = [name.lower() for name in requested_authors]

    # Create a new list of authors with their index corresponding memes and quote counts
    authors, memes, quotes = list(), list(), list()

    # Iterate over the scoreboard dictionary and append the author, along with meme/quote counts to their lists if
    # they are the requested author or there was no specific request
    for author, (quote, meme) in sorted(scoreboard.items(), key=lambda item: sum(item[1])):
        if requested_authors is None or author.lower() in requested_authors:
            authors.append(author)
            memes.append(meme)
            quotes.append(quote)

    # Then create a new np array of 1..authors and then an offset array for the quotes
    meme_column = np.arange(len(authors))
    quotes_column = meme_column + .25

    # Get the figure and axis of the plot
    fig, ax = plt.subplots()

    # Add two bar plots, one for the memes and on for the quotes for a single author
    ax.barh(meme_column, memes, color='#1f85de', height=.25, edgecolor='white', label='Memes')
    ax.barh(quotes_column, quotes, color='#f33b2f', height=.25, edgecolor='white', label='Quotes')

    # Create the labels for each of the axes
    plt.xlabel('Count', labelpad=15, fontweight='bold', labelsize=15)
    plt.ylabel('People', labelpad=15, fontweight='bold', labelsize=15)

    # Then center each of the persons names between the two bar plots and giv ethe plot a title
    plt.yticks(meme_column + .125, authors)
    plt.title('Bruh Bot Scoreboard', pad=15, fontweight='bold')

    # Remove a lot of the ugly spines from the original graph that matplotlib gives us
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD')

    # Remove the ticks for the persons names and graph count
    ax.tick_params(bottom=False, left=False)

    # Finally some beatifying of the axes and tightening the layout to be more compact
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color='#EEEEEE')
    ax.yaxis.grid(False)

    # Then finally resize the matplotlib graph and make sure it fills the entire screen before saving and sending it
    fig.set_size_inches(18., 14.)
    fig.tight_layout()

    # Show the legend so we know what each bar stands for and then save the image to the filesystem
    plt.legend()
    plt.savefig('scoreboard.jpg')

    # Then finally send the finished image in the discord server that requested it
    await ctx.channel.send(file=discord.File('scoreboard.jpg'))

    # Then remove from the filesystem to prevent clutter
    os.remove('scoreboard.jpg')


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
