# baseball_data

Ben Kite

2017-01-05

This is my collection of Python scripts that pull baseball data from
the internet in fun ways.  I looked at baseball-reference.com and came
up with some ways that I wanted to combine their data across multiple
pages. Here I outline what each script does.

dataScrape.py: 
Uses Beautiful Soup to scrape data from html and put
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
