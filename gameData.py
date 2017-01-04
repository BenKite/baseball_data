## Ben Kite
## 2016-04-22

import pandas, os
from dataScrape import finder

import pymysql.cursors

def YearData(year, directory):
    year = str(year)

    if not os.path.exists(directory):
        os.makedirs(directory)

    dataBase = dict()

    teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL',
             'DET', 'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY',
             'OAK', 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR',
             'WSN']

    for tm in teams:
        try:
            dataBase[tm] = finder(tm, year)
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

## Now the function is defined
## Create a directory to catch the data files and fill it up

directory = "data/"

if not os.path.exists(directory):
    os.makedirs(directory)

## Now pull years
years = (2015, 2016)
datdic = dict()
for y in years:
    datdic[y] = (YearData(y, directory))


