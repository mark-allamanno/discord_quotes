import discord

import csv
from collections import defaultdict
from heapq import nlargest
from typing import Dict, Tuple, List
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from commands import *


@BOT.command(name='leaderboard', brief='Sends the overall number of memes/quotes associated with each person')
@lock_to_channel(CHANNEL_LOCK)
def get_statistics_dict() -> Dict[str, Tuple[int, int]]:
    """
    Get the total count of each person's quotes and memes in the database as a dictionary of the form
    Name -> (# Quotes, # Memes) so that this can then be used by the scoreboard functions to make pretty matplotlib
    graphs to send in the chat

    Parameters:
        Nothing

    Returns:
        scoreboard - A dictionary linking all peoples names to a tuples of (# Quotes, # Memes) counters
    """

    # Declare default dictionary of peoples names to their quote/meme counts
    scoreboard = defaultdict(lambda: (0, 0))

    # Open the csv file of all of the quotes inside of it
    with open(CSV_FILE, 'r') as college_quotes:

        # Get every component of every line in the csv file as we need to check each line for its authors
        for quote in csv.reader(college_quotes):
            for index in range(1, len(quote), 2):

                # If we are on the author's index then parse all authors in the quote and change their meme count-
                for author in quote[index].split(' & '):
                    quotes, memes = scoreboard[author]
                    scoreboard[author] = quotes + 1, memes

    # Iterate over all the meme folders and update each authors count with the number of memes in their folder
    for author in Path(MEMES_PATH).iterdir():
        quotes, memes = scoreboard[author.stem.title()]
        scoreboard[author.stem.title()] = quotes, len(list(author.iterdir()))

    # Then return the completed dictionary of statistics in the form Name -> (# Quotes, # Memes)
    return scoreboard


async def get_statistics(ctx, *args) -> None:
    """
    Send back a graph that represents the current number of quotes/memes for each person in the database. This
    command though has many options to get just what you want. So you can either rtype in $leaderboard to get everyone's
    total contributions as a bar chart. You could optionally add pie after $leaderboard to give a pie chart of the
    relative contributions of everyone. Or add a number, $Leaderboard n to display the bar chart but only the top n
    members. Or finally you could instead input a list of names to only get the stats for the specified people.
    like $leaderboard bob mary jane.

    Parameters:
        ctx - The context from which this command was send
        args - the arguments to the scoreboard function to customize it to be what the user wants

    Returns:
        Nothing
    """

    scoreboard_info = get_statistics_dict()  # Get the scoreboard in the form Name -> (# Quotes, # Memes)

    # If there are no more arguments then just send the base leaderboard with everyone in it
    if len(args) == 0:
        await send_leaderboard_image(ctx, scoreboard_info)

    # If the user wants to see the ratios then send a pie chart with the percentages of each user
    elif args[0] == 'pie':
        await pie_chart_scoreboard(ctx, scoreboard_info)

    # If the user is requesting to see the leaderboard of only the top n people then send that instead
    elif len(args) == 1 and args[0].isdigit():
        await send_leaderboard_image(ctx, scoreboard_info, top_n_authors=int(args[0]))

    # Maybe they are trying to only see the leaderboard for a couple of people in which case only show those people
    elif all([name.title() in scoreboard_info for name in args]):
        await send_leaderboard_image(ctx, scoreboard_info, requested_authors=args)

    # Otherwise they messed something up so let them know
    else:
        await ctx.channel.send("Malformed leaderboard query, cannot complete request")


async def pie_chart_scoreboard(ctx, scoreboard: Dict[str, Tuple[int, int]]) -> None:
    """
    This is another version of the barchart scoreboard below this, however this one is concerned with the
    percentage ratios of everyone's participation in the server, not the raw numbers. So it will show us relatively
    who is the most active among everyone in a more direct manner.

    Parameters:
        ctx - The context from which this command was send
        scoreboard - A dictionary linking all peoples names to a tuples of (# Quotes, # Memes) counters

    Returns:
        Nothing
    """

    async def send_pie_chart(authors: List[str], contributions: List[int], content_type: str) -> None:
        """
        A quick async function that takes in a list of authors and their corresponding counts for quotes/memes
        and will create a nice and pretty pie chart from this and send it in the chat for fun. Most of the styling for
        this graph was taken form the website below.

        Parameters:
            authors - A list of strings of all of the authors in the server
            contributions - A list of numbers of their total contribution count to the server
            content_type - The type of content this is counting so either memes or quotes

        Returns:
            Nothing

        References:
            https://medium.com/@kvnamipara/a-better-visualisation-of-pie-charts-by-matplotlib-935b7667d77f
        """

        slice_colors = ['#7fe5f0', '#407294', '#ff7373', '#8a2be2', '#7fffd4', '#ffd700', '#5ac18e',
                        '#947fff', '#f0f0f0', '#f190c1', '#f9ae54', '#bb6c5d', '#924431', '#2e465e',
                        '#fadb6a', '#4dacb4', '#6b724', '#d28a2d']

        # This part minus the header was taken from the website referenced above
        fig1, ax1 = plt.subplots()

        # Plot fht pie char on the matplotlib lib surface
        ax1.pie(contributions, colors=slice_colors, labels=authors, autopct='%1.1f%%', startangle=90,
                pctdistance=0.85, labeldistance=1.05, textprops={'fontsize': 19})
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')

        # Then set a title so people know what this represents
        plt.title(f'Total {content_type} Contributions', pad=20, fontweight='bold', fontsize=30)

        # Then add the center circle to the axis so we only have the outer edges
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        # Make sure it is drawn as a circle and then tighten the layout
        fig.set_size_inches(18., 14.)
        ax1.axis('equal')
        plt.tight_layout()

        # Then finally save the quote pie chart and send it in chat and delete the file from
        # the system
        plt.savefig('quote_percentages.jpg')
        await ctx.channel.send(file=discord.File('quote_percentages.jpg'))
        os.remove('quote_percentages.jpg')

    # Get all of the authors as we need them for labeling
    total_quotes = sum([quotes for quotes, _ in scoreboard.values()])
    total_memes = sum([memes for _, memes in scoreboard.values()])

    # Create a bunch of variables for the quotes, authors and misc for each quotes and memes category
    num_quotes, quote_authors, misc_quotes = list(), list(), 0
    num_memes, meme_authors, misc_memes = list(), list(), 0

    # Then get the number of quotes for each author and plot it and send it in chat
    for author, (quotes, memes) in scoreboard.items():

        # If the user has less than 2% participation in quotes then group them into misc. otherwise add them
        if .02 < quotes / total_quotes:
            quote_authors.append(author)
            num_quotes.append(quotes)
        else:
            misc_quotes += quotes

        # If the user has less than 2% participation in memes then group them into misc. otherwise add them
        if .02 < memes / total_memes:
            meme_authors.append(author)
            num_memes.append(memes)
        else:
            misc_memes += memes

    # Then append all of the misc quotes that were very small fractions of the whole
    num_quotes.append(misc_quotes)
    quote_authors.append('Misc.')

    # Then append all of the misc quotes that were very small fractions of the whole
    num_memes.append(misc_memes)
    meme_authors.append('Misc.')

    # Finally send both pie charts in chat so we can all compare our contributions
    await send_pie_chart(quote_authors, num_quotes, 'Quote')
    await send_pie_chart(meme_authors, num_memes, 'Meme')


async def send_leaderboard_image(ctx, scoreboard: Dict[str, Tuple[int, int]], requested_authors=None,
                                 top_n_authors=0) -> None:
    """
    A relatively long function that parses the raw scoreboard data into a matplotlib graph and then sends that
    graph in the querying channel. This version is a bar graph and is relatively modular in that it can send
    only a few people or everyone or only the top n people etc.

    Parameters:
        ctx - The context from which this command was send
        scoreboard - A dictionary linking all peoples names to a tuples of (# Quotes, # Memes) counters
        requested_authors - A list of requested authors, if blank then just get everyone
        top_n_authors - An int representing we want the top n authors, if none then just get everyone

    Returns:
        Nothing
    """

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
    plt.xlabel('Count', labelpad=15, fontweight='bold', fontsize=20)
    plt.ylabel('People', labelpad=15, fontweight='bold', fontsize=20)

    # Then center each of the persons names between the two bar plots and giv ethe plot a title
    plt.xticks(fontsize=15)
    plt.yticks(meme_column + .125, authors, fontsize=15)
    plt.title('Bruh Bot Scoreboard', pad=15, fontweight='bold', fontsize=30)

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
