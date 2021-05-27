import csv
import random
from typing import List, Tuple
from pathlib import Path

from commands import *


def all_quotes_by(author: str) -> List[Tuple[str]]:
    """
    Get all the quotes by a specified person, removing from the possible pool all quotes that have been seen on this
    rotation of the quote cycle. Meaning we cannot re-see a quote until we have gone through all of their quotes first.
    Returns a list of tuples of a person's quotes

    Parameters:
        author - The name of the author to get all of the unseen quotes for

    Returns:
        quotes - A list of tuples of all quotes by this author that are currently unseen
    """

    with open(CSV_FILE, 'r') as college_quotes:

        all_quotes = set()  # Create a new set of all he quotes that involve this person

        # Get all of the quotes of the specific person and remove any duplicate quotes
        for quote in csv.reader(college_quotes):
            if author == 'random' or any(author.title() in quote[i] for i in range(1, len(quote), 2)):
                all_quotes.add(tuple(quote))

        # Remove all of the seen quotes from the retrieved quotes
        remove_duplicates = all_quotes - SEEN_QUOTES

        # If every quote of theirs has already been sent then remove them all from seen and return all their quotes
        if not remove_duplicates:
            SEEN_QUOTES -= all_quotes
            return list(all_quotes)

        # Otherwise just return the new and fresh quotes to prevent stagnant quoting
        return list(remove_duplicates)


@BOT.command(name='add-quote', brief='Adds a new quote to the database given a quote and an author')
@lock_to_channel(CHANNEL_LOCK)
async def save_quote(ctx, *quote) -> None:
    """
    Adds a specified quote to the database CSV file. Can take in a variable amount of quote/author pairs but it
    should be of the form "quote" author "quote" author or else we cannot parse it correctly so follow this formatting
    exactly as specified

    Parameters:
        ctx - The context from which this command was send
        quote - A tuple of strings of variable length that is the quote to add to the database

    Returns:
        Nothing
    """

    # Make sure the length of the arguments parameter makes sense before attempting to add it
    if len(quote) % 2:
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


@BOT.command(name='delete-quote', brief='Removes a mistyped or mis-associated quote from the database')
@lock_to_channel(CHANNEL_LOCK)
async def remove_quote(ctx, *quote) -> None:
    """
    Removes a specified quote from the database in the case of a typo or semi-duplicate quote. To use you need to
    type in the $delete-quote command and then use the format "quote" author "quote" author to remove that quote
    from the database. It doesnt have to be the whole quote, just enough to uniquely identify it, only one
    person can use this because it comes with great responsibility.

    Parameters:
        ctx - The context from which this command was send
        quote - A tuple of strings of variable length that is the quote to remove from the database

    Returns:
        Nothing
    """

    # Make sure the user that we want is making these edits to the database
    if ctx.message.author.name != 'Bob the Great':
        await ctx.channel.send(f"Nice try, {ctx.message.author.mention}, but this is only for emergencies")
        return

    # If the user didnt input any arguments or they input an odd number of arguments then the query is strange,
    # so dont parse it
    if len(quote) == 0 or len(quote) % 2 == 1:
        await ctx.channel.send("You either didn't give a quote to delete or the quote's formatted was malformed.")
        return

    partial_quote = list(quote)  # Convert the arguments to a list so we can check for sublist

    with open(CSV_FILE, 'r') as quotes_read, open('college-quotes-edited.csv', 'w') as quotes_write:

        # Open a new CSV writer and create a boolean to track the removed quote
        csv_writer = csv.writer(quotes_write, quoting=csv.QUOTE_ALL)
        quote_removed = False

        # Read every line from the original csv file and only write it to the new one of it does not match the quote to
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


@BOT.command(name='quote', brief='Fetches a random quote by a specified person or anyone if left unfilled')
@lock_to_channel(CHANNEL_LOCK)
async def get_quote(ctx, quote_author='random') -> None:
    """
    Get a random quote by the person specified in the argument. Searched the database for quotes by them and
    returns sends a random one back as a response. The format should be $quote author where author is the person
    you would like to quote

    Parameters:
        ctx - The context from which this command was send
        quote_author - The string of the person that we want to get a quote from the database for

    Returns:
        Nothing
    """

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
