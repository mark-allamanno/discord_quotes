from discord.ext import commands
import discord

import dotenv

import os
import csv
import random
from pathlib import Path
from collections import defaultdict


# Create a new bot with the prefix of '$'
BOT = commands.Bot(command_prefix='$')

# Load the environment variables and then get the discord api token
dotenv.load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Get the database and memes folder directories from the .env file
CSV_FILE = os.getenv('DATABASE_PATH')
MEMES_PATH = os.getenv('MEMES_FOLDER')

# Get the channel that we are locking the bot to
CHANNEL_LOCK = os.getenv('CHANNEL_LOCK')

# Get the filename of the leaderboard image to send in the chat
TEMP_FILE_NAME = os.getenv('LEADERBOARD_NAME')

# Then finally declare a set of seen quotes at this point in time
SEEN_QUOTES = set()
SEEN_MEMES = set()


def lock_to_channel(channel):
    """Short decorator function to lock these commands to the channel we decide present in the .env file"""

    return commands.check(lambda ctx: ctx.channel.name == channel)


def all_quotes_by(author):
    """Get all the quotes by a specified person. Returns a list of lists of a person's quotes"""

    global SEEN_QUOTES  # Use the global seen quotes variable

    with open(CSV_FILE, 'r') as quotes:

        # Get all of the quotes of the specific person and remove any duplicate quotes
        all_quotes = {tuple(q) for q in csv.reader(quotes) if author == 'random' or author.title() in q}
        remove_duplicates = all_quotes - SEEN_QUOTES

        # If every quote of theirs has already been sent then remove them from seen and return all their quotes
        if not remove_duplicates:
            SEEN_QUOTES -= all_quotes
            return list(all_quotes)

        # Otherwise just return the new and fresh quotes
        return list(remove_duplicates)


def get_statistics_dict():
    """Get the total count of each person's quotes and memes in the database as a dictionary of the form """
    """Name -> (#Quotes, #Memes)"""

    # Declare default dictionary of peoples names to their quote/meme counts
    scoreboard = defaultdict(lambda: (0, 0))

    # Open the csv file of all of the quotes inside of it
    with open(CSV_FILE, 'r') as college_quotes:
        
        # Get every line in the csv file as we need to check each line for its authors
        for quote in csv.reader(college_quotes):

            # Then iterate over all of the components of the quote ie quote body and author 
            for index, author in quote:

                # The authors are always on odd indices in teh database so only increment the quote count for valid people
                if index % 2 == 1:
                    quotes, memes = scoreboard[author]
                    scoreboard[author] = quotes + 1, memes
    
    # Then iterate over the meme directory and increment the number of memes by the directiry size
    for author in Path(MEMES_PATH).iterdir():

        # Title the author so we can ensure that it will match the format present in the quotes file
        author = author.name.title()

        # Then get the current quote / meme count and assign it a new value
        quotes, memes = scoreboard[author]
        scoreboard[author] = quotes, len(list(Path(MEMES_PATH, author).iterdir()))
    
    return scoreboard


@BOT.command(name='summon-him', brief='Summons Picklechu from the void')
@lock_to_channel(CHANNEL_LOCK)
async def summon_picklechu(ctx):
    """Sends a picture of Picklechu in chat so everyone can know fear"""

    await ctx.channel.send(file=discord.File(str(Path(MEMES_PATH, 'general', 'picklechu.png'))))


@BOT.command(name='add-quote', brief='Command to add a new quote to the database')
@lock_to_channel(CHANNEL_LOCK)
async def save_quote(ctx, *args):
    """Adds a specified quote to the CSV file. Can take in a variable amount of arguments but the format should be """
    """"quote" author "quote" author..."""

    # Make sure the length of the arguments parameter makes sense before attempting to add it
    if len(args) % 2 == 1:
        await ctx.channel.send('Why is the number of input arguments odd? It should always be even!')
        return

    with open(CSV_FILE, 'a') as quotes:

        # Open a new CSV writer and then write the quote surrounded by quotation marks to the college_quotes.csv file
        writer = csv.writer(quotes, quoting=csv.QUOTE_ALL)
        writer.writerow([s.title() if i % 2 else s for i, s in enumerate(args)])

        # Then send a confirmation message so the user knows it was added
        await ctx.channel.send('Successfully added quote to database! Your lapse in judgement has been immortalized.')


@BOT.command(name='delete-quote', brief='Command to remove a mistyped quote from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_quote(ctx, *args):

    # If the user didnt input any arguments or they input an odd number of arguments then the query is strange,
    # so dont parse it
    if len(args) == 0 or len(args) % 2 == 1:
        await ctx.channel.send(f"You either didn't give a quote to delete or the quote's formatted was malformed.")
        return

    partial_quote = list(args)  # Convert the arguments to a list so we can check for sublist

    # Open the old csv file we are altering and a new one with the quote removed
    with open(CSV_FILE, 'r') as quotes_read, open('college-quotes-edited.csv', 'w') as quotes_write:

        # Open a new CSV writer and create a boolean to track the removed quote
        csv_writer = csv.writer(quotes_write, quoting=csv.QUOTE_ALL)
        quote_removed = False

        for row in csv.reader(quotes_read):
            
            # If the partial quote matches this one line by line then dont write it and let us know we removed the quote
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
        await ctx.channel.send("Quote was not found in the database, are you sure you it is correct?")


@BOT.command(name='quote', brief='Command to fetch a quote by a specified person or anyone if left unfilled.')
@lock_to_channel(CHANNEL_LOCK)
async def get_quote(ctx, quote_author='random'):
    """Get a random quote by the person specified in the argument. Searched the database for quotes by them and """
    """returns sends a random one back as a response"""

    # Get all the quotes by a specific person and then choose how to handle it
    quotes_list = all_quotes_by(quote_author)

    if quotes_list:     # Make sure the requested author has quotes to search

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
        await ctx.channel.send(f'{quote_author} not found in the database!')


@BOT.command(name='add-meme', brief='Command to add meme to the database associated with a specific person.')
@lock_to_channel(CHANNEL_LOCK)
async def save_meme(ctx, author, *filenames):
    """Saves memes with given filenames to the servers meme archive"""

    author = author.lower()   # Make sure the author's name is lowercase for homogeneity

    # If the path to the user doesnt exist then we need to create it to prevent issues later
    if not Path(MEMES_PATH, author).exists():
        Path(MEMES_PATH, author).mkdir()

    for attachment, file in zip(ctx.message.attachments, filenames):

        # Create a valid filename with extension for the file and get all filenames already present in the directory
        filename = f'{file}{Path(attachment.filename).suffix}'
        present_files = [name.stem for name in Path(MEMES_PATH, author).iterdir()]

        # Then upload the file only if it has a unique name otherwise let the user know it failed
        if filename not in present_files:
            await attachment.save(str(Path(MEMES_PATH, author, filename)))
        else:
            await ctx.channel.send(f'Filename, {filename}, for user {author} is already taken, try again!')

    # Then let the user know we have saved the meme successfully
    await ctx.channel.send('Meme has been saved to the archive for future use')


@BOT.command(name='delete-meme', brief='Command to remove a mistyped or mis-associated meme from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_meme(ctx, author=None, filename=None):

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
            meme_file.unlink()
            await ctx.channel.send(f"Meme {meme_file} was remove from {author}'s meme folder sucessfully")
            return
    
    # If we make it here then we never found the file to remove, so something is wrong. Let the user know
    await ctx.channel.send(f"Meme was not present in {author}'s directory, are you sure this is the right name?")


@BOT.command(name='meme', brief='Command to send back a meme associated with a specified person.')
@lock_to_channel(CHANNEL_LOCK)
async def get_meme(ctx, author='random'):
    """Send back a meme that is associated with a given author if they exist in the database"""

    global SEEN_MEMES   # Use the global seen memes variable

    author = author.lower()  # Make sure the author's name is lowercase for homogeneity

    # Then make sure the author exists in the database before pulling a meme
    if not Path(MEMES_PATH, author).exists() and author != 'random':
        await ctx.channel.send(f'{author} has no memes associated with them.')
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
async def get_statistics(ctx, *args):
    """Send back a matplotlib image that represents the current number of quotes/memes for each person in the database"""
    
    scoreboard_info = get_statistics_dict() # Get the scoreboard in the form Name -> (# Quotes, # Memes)
    
    if len(args) == 0:
        # Raw leaderboard data of everyone
        pass

    elif len(args) == 2 and args[0].isdigit() and (args[1] == 'memes' or args[1] == 'quotes'):
        # Top n statistics
        pass

    elif len(args) == 1 and args[0] in scoreboard_info:
        # Single person statistics
        pass

    else:
        await ctx.channel.send("Malformed leaderboard query, cannot complete request")
    

@BOT.event
async def on_ready():
    """When the client connects to the discord server print out a confirmation message and change presence"""

    print(f'Connected to Discord Successfully!')

    await BOT.change_presence(
        status=discord.Status.online, 
        activity=discord.Activity(type=discord.ActivityType.watching, name='Tingledorf')
    )


if __name__ == '__main__':
    BOT.run(TOKEN)
