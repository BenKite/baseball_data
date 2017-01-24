#!/usr/bin/env python3

## Ben Kite
## 2017-01-05

"""
Finds all game played in the year that you specify and saves
their results in a single .csv file.

The output file will be named with the year followed by "Games.csv".

"""

import pandas, os, argparse
from dataScrape import pullGameData

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--year", help="Year of games to be collected. Eventually I'll allow multiple years (e.g., 2010-2012 or 2010 2012 2013, etc.)")
parser.add_argument("--datdir", help="Name of directory where the data should be stored.  If the directory does not exist it will be created. Defaults to data/", default = "data/")

args = parser.parse_args()

year  = str(args.year)
directory = str(args.datdir)

def YearData(year, directory):
    year = str(year)

    if not os.path.exists(directory):
        os.makedirs(directory)

    dataBase = dict()

    teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
             'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
             'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

    for tm in teams:
        try:
            dataBase[tm] = pullGameData(tm, year)
        except IndexError:
            pass

    gameData = pandas.concat(dataBase)

    gameData.rename(columns = {"Team" :"HomeTeam", 
                               "Opp":"AwayTeam", 
                               "Record":"HomeRecord",
                               "Runs":"RunsHome", 
                               "OppRuns":"RunsAway",  
                               "WL":"HomeWL",  
                               "Streak":"HomeStreak"}, inplace = True)
   
    gameData = gameData.sort_values(["Date"])

    gameData = gameData.drop("gamenum", axis = 1)
    gameData = gameData.drop("gamenum2", axis = 1)
    gameData = gameData.drop("boxscore", axis = 1)

    homeData = gameData[gameData["Location"] != "@"]

    homeData = homeData.drop("Location", axis = 1)

    homeData["Index"] = range(0, len(homeData))

    outfile = directory + year + "Games.csv"

    homeData["year"] = year

    homeData.to_csv(outfile, index = False, encoding = "utf-8")
    return(homeData)

## Now the function is defined, use it

YearData(year, directory)


