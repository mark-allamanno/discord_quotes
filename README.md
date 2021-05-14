# FoGG Discord Bot

A relatively simple discord bot for the Friend of Galileo Gang (FoGG), dubbed Bruh Bot, for use in our friend groups 
server. It is mostly used to add and dispense quotes and memes amassed through our gatherings but is also used as a reminder
system and for teasing friends. Quotes are exactly what you think they were, quotes said by anyone in the group that we 
thought were memorable enough to keep around. Memes on the other hand are images or videos that are too good to lose.
It currently runs off of a Raspberry Pi in our dorm room.

## Commands

### Quote Related Commands

``$add-quote "quote" author "quote" author...``

A command for any of us to add a new single or multi quote to the discord bot. A single quote refers to
a single quote author pair, but a multiquote refers to many quote author pairs in the case of a more
involved exchange. Used to immortalize the foolishness of our group as a whole.

``$add-quote author``

A command for any of us to fetch a single or multi quote from the discord bot. If given a second argument
it will search for that person in the database and only send back a quote authored by that person. If left
blank though it will just grab a random quote from anyone. Used to relive the foolishness of the group.

``$remove-quote "quote" author "quote" author...``

A privileged command that can only be used by the server admins that should only be used in the case of
a quoting goof or mis-attribution, it will take in a quote of the same format as the add-quote command
and remove it from the bot forever.

### Meme Related Commands

``$add-meme filename1 filename2...``

A command for any of us to add a new meme to the discord bot. It takes in an author of the memes and a list
of filenames to save the attached memes under, in sequence. To use you must type in this command, attach
all the memes you would like to save and then give a list fo filenames to save these memes as in the users 
folder. Used to immortalize the foolishness of our group as a whole.

``$add-meme author``

A command for any of us to fetch a meme from the discord bot. If given a second argument
it will search for that person in the database and only send back a meme authored by that person. If left
blank though it will just grab a random meme from anyone. Used to relive the foolishness of the group.

``$remove-meme author filename``

A privileged command that can only be used by the server admins that should only be used in the case of
a quoting goof or mis-attribution, it will take in an author, and a filename of a meme to delete, and it 
will remove it from that person's meme folder forever.

### Statistics Commands

``$leaderboard |pie| |n_larget| |name1 name2|``

A command to see the current statistics for the discord bot ie how many quotes or memes people have associated
with them, and it has a couple of options to make is easier to see what your interested in. When ``$leaderboard n``
is entered it will create bar chart of only the top n authors overall, when ``$leaderboard name1 name2`` it will display
a bar chart containing only the people whose names are mentioned in the command. Finally ``$leaderboard pie``
will create a pie chart of the relative frequency of each person in the database, giving the relative percentages
of each person for the memes and quotes categories respectively.

## Misc. Utilities

### Backups 

There are also two extra files in teh repo called ``backup_memes.py`` and ``backup_quotes.py`` which will
be scheduled via crontab to run once a day at 5pm. When they run they will back up the memes to my Google
Drive in a folder called 'Bruh Bot Database' and will backup the quotes to a Google Sheet called 
'College Quotes.csv'. THis is to ensure that is something were to ever happen to the raspberry pi that 
we would have up to date backups of everything we added so far and can easily restore it.

### Reminders

Finally, the last file left is ``reminders.py`` which is also schedules daily via crontab which will send 
reminders in the server for us to take scheduled breaks since some people in the friend group need a little
help remembering to take breaks.

## Dependencies

```Pydrive 2 - For Google Drive API integration 
Gspread - For Google Sheets API integration
Discordpy - For Discord API integration
Matplotlib - For sending the statical graphs about participation
Numpy - For assisting in the creation of the statistical graphs
Pillow - For one of the reminders which will send a meme
dotenv - For loading in environment variables to keep API keys and secrets private```
