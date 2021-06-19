import discord

import csv
from collections import defaultdict
from heapq import nlargest
from typing import Dict, Tuple, List
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from commands import *


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

    scoreboard = defaultdict(lambda: (0, 0))

    with open(CSV_FILE, 'r') as college_quotes:

        for quote in csv.reader(college_quotes):
            for index in range(1, len(quote), 2):
                for author in quote[index].split(' & '):
                    quotes, memes = scoreboard[author]
                    scoreboard[author] = quotes + 1, memes

    for author in Path(MEMES_PATH).iterdir():
        quotes, memes = scoreboard[author.stem.title()]
        scoreboard[author.stem.title()] = quotes, len(list(author.iterdir()))

    return scoreboard


@BOT.command(name='leaderboard', brief='Sends the overall number of memes/quotes associated with each person')
@lock_to_channel(CHANNEL_LOCK)
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

    if len(args) == 0:
        await send_leaderboard_image(ctx, scoreboard_info)

    elif args[0] == 'pie':
        await pie_chart_scoreboard(ctx, scoreboard_info)

    elif len(args) == 1 and args[0].isdigit():
        await send_leaderboard_image(ctx, scoreboard_info, top_n_authors=int(args[0]))

    elif all([name.title() in scoreboard_info for name in args]):
        await send_leaderboard_image(ctx, scoreboard_info, requested_authors=args)

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

        fig1, ax1 = plt.subplots()
        ax1.pie(contributions, colors=slice_colors, labels=authors, autopct='%1.1f%%', startangle=90,
                pctdistance=0.85, labeldistance=1.05, textprops={'fontsize': 19})
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')

        plt.title(f'Total {content_type} Contributions', pad=20, fontweight='bold', fontsize=30)

        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)
        fig.set_size_inches(18., 14.)
        ax1.axis('equal')
        plt.tight_layout()

        plt.savefig('quote_percentages.jpg')
        await ctx.channel.send(file=discord.File('quote_percentages.jpg'))
        os.remove('quote_percentages.jpg')

    total_quotes = sum([quotes for quotes, _ in scoreboard.values()])
    total_memes = sum([memes for _, memes in scoreboard.values()])

    num_quotes, quote_authors, misc_quotes = list(), list(), 0
    num_memes, meme_authors, misc_memes = list(), list(), 0

    for author, (quotes, memes) in scoreboard.items():

        if .02 < quotes / total_quotes:
            quote_authors.append(author)
            num_quotes.append(quotes)
        else:
            misc_quotes += quotes

        if .02 < memes / total_memes:
            meme_authors.append(author)
            num_memes.append(memes)
        else:
            misc_memes += memes

    num_quotes.append(misc_quotes)
    quote_authors.append('Misc.')

    num_memes.append(misc_memes)
    meme_authors.append('Misc.')

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

    if top_n_authors:
        scoreboard = {x: scoreboard[x] for x in nlargest(top_n_authors, scoreboard, key=lambda x: sum(scoreboard[x]))}

    if requested_authors:
        requested_authors = [name.lower() for name in requested_authors]

    authors, memes, quotes = list(), list(), list()

    for author, (quote, meme) in sorted(scoreboard.items(), key=lambda item: sum(item[1])):
        if requested_authors is None or author.lower() in requested_authors:
            authors.append(author)
            memes.append(meme)
            quotes.append(quote)

    meme_column = np.arange(len(authors))
    quotes_column = meme_column + .25

    fig, ax = plt.subplots()

    ax.barh(meme_column, memes, color='#1f85de', height=.25, edgecolor='white', label='Memes')
    ax.barh(quotes_column, quotes, color='#f33b2f', height=.25, edgecolor='white', label='Quotes')

    plt.xlabel('Count', labelpad=15, fontweight='bold', fontsize=20)
    plt.ylabel('People', labelpad=15, fontweight='bold', fontsize=20)

    plt.xticks(fontsize=15)
    plt.yticks(meme_column + .125, authors, fontsize=15)
    plt.title('Bruh Bot Scoreboard', pad=15, fontweight='bold', fontsize=30)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_color('#DDDDDD')

    ax.tick_params(bottom=False, left=False)

    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color='#EEEEEE')
    ax.yaxis.grid(False)

    fig.set_size_inches(18., 14.)
    fig.tight_layout()

    plt.legend()
    plt.savefig('scoreboard.jpg')

    await ctx.channel.send(file=discord.File('scoreboard.jpg'))
    os.remove('scoreboard.jpg')
