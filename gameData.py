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

    gameData.rename(columns = {0 :"gamenum", 1 :"gamenum2", 2 :"Date",
                              3 :"boxscore", 4 :"HomeTeam", 5:"Location", 6:"AwayTeam", 7:"HomeRecord",
                              8:"RunsHome", 9:"RunsAway", 10:"Inn", 11:"HomeWL", 12:"Rank", 13:"GB",
                              14:"Win", 15:"Loss", 16:"Save", 17:"Time", 18:"DN", 19:"Attendance",
                              20:"HomeStreak"}, inplace = True)
   
    gameData = gameData.sort_values(["Date"])

    gameData = gameData.drop("gamenum", axis = 1)
    gameData = gameData.drop("gamenum2", axis = 1)
    gameData = gameData.drop("boxscore", axis = 1)

    homeData = gameData[gameData["Location"] != "@"]


    AwayWL = []
    AwayStreak = []
    for row in range(0, len(homeData)):
        date = homeData["Date"][row]
        hometeam = homeData["HomeTeam"][row]
        awayteam = homeData["AwayTeam"][row]
        tmprow = gameData.loc[(gameData["HomeTeam"] == awayteam) & (gameData["AwayTeam"] == hometeam)
        & (gameData["Location"] == "@") & (gameData["Date"] == date)]
        AwayWL.append(tmprow["HomeWL"][0])
        AwayStreak.append(tmprow["HomeStreak"][0])

    NAwayWL = []
    for i in range(0, len(AwayWL)):
        tmp = AwayWL[i].split("-")
        win = tmp[0]
        loss = tmp[1]
        if(int(homeData["RunsAway"][i]) > int(homeData["RunsHome"][i])):
            NAwayWL.append(str(int(win) - 1) + "-" + str(loss))
        else:
            NAwayWL.append(str(win) + "-" + str(int(loss) - 1))

    NHomeWL = []
    for i in range(0, len(homeData["HomeWL"])):
        tmp = homeData["HomeWL"][i].split("-")
        win = tmp[0]
        loss = tmp[1]
        if(int(homeData["RunsHome"][i]) > int(homeData["RunsAway"][i])):
            NHomeWL.append(str(int(win) - 1) + "-" + str(loss))
        else:
            NHomeWL.append(str(win) + "-" + str(int(loss) - 1))

    homeData["AwayWL"] = NAwayWL
    homeData["HomeWL"] = NHomeWL
    homeData["AwayStreak"] = AwayStreak

    Streak = []
    for i in AwayStreak:
        Streak.append(i[0] + str(len(i)))

    homeData["AwayStreak"] = Streak

    Streak = []
    for i in homeData["HomeStreak"]:
        Streak.append(i[0] + str(len(i)))

    homeData["HomeStreak"] = Streak

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
    y = 2016
    datdic[y] = (YearData(y, directory))


