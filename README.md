# baseball_data

Ben Kite

2017-01-15

This is my collection of Python scripts that pull baseball data from
the internet in fun ways.  I looked at baseball-reference.com and came
up with some ways that I wanted to combine their data across multiple
pages. Here I outline what each script does. 

dataScrape.py: 
Uses BeautifulSoup to scrape data from html and put
them in pandas data frames.  This is where I will keep all of my data
scraping functions.  I will work on adding comments explaining what is
being done with the webpages.

gameData.py: 
I wanted a dataset for a given year that has basic
information for all games played (teams involved, scores, winner,
loser, save, attendence, etc.).  I searched for this for about 30
seconds, and then I gave up and saw this as a fun opportunity work on
some Python.  I used the “finder” function in dataScrape.py to pull
out the data from each teams page for the year I want.  These datasets
have all of the 162 (more if theres postseason play) for that team.  I
stacked all 30 datasets together, removed the duplicate games (I only
used the home games from each team’s page), cleaned up the variable
names to make a bit more sense, and then saved the final product in a
.csv file.  This now can run directly in a command line.

playerData.py:
I also wanted to pull data summarizing individual seasons for players.
This script pull data on batting and pitching from 5 different tables
that are found on a teams page of a given year.  See the help info ($
python playerData.py --help) for instructions.

boxScores.py:
This pulls out box score information for individuals games for a team
for an entire season. It first looks at the team page to see when the
games were, and then it uses those dates to pull individual box
scores.

battingOverTime.py:
Uses the box score data to create plots to show how players batting
ability changes over the course of the season. This now runs from the
command line.
