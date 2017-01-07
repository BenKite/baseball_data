#!/usr/bin/env python3

## Ben Kite
## 2016-04-22

"""
Pulls all boxscores for a team for a single season.  Requires user to provide the team and the year.

The teams are indicated by providing one of the following abreviations:
['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 
 'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 
 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

This can take up to six minutes to run for a single team!  I'm going to work toward this having an update option so that data can be scraped during the course of a season and quickly added to a .csv file. 

Running the following would give you all boxscores for the Yankees in 2010:

$ python boxScores.py --team NYY --year 2010

"""

import pandas, os, numpy, argparse
from dataScrape import finder
import requests, bs4, re

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--team", help="Name of team from which you want to collect data.")
parser.add_argument("--year", help="Year of games to be collected")

args = parser.parse_args()

year  = str(args.year)
team = str(args.team)

datdir = "data/BoxScores/"

## Write code to read the boxscore for a game

def Quantify (x):
    out = []
    for i in x:
        if len(i) < 1:
            out.append(None)
        else:
            out.append(float(i))
    return(out)

def GameFinder (gameInfo):
    teamNames = {"KCR":"KCA",
                 "CHW":"CHA",
                 "CHC":"CHN",
                 "LAD":"LAN",
                 "NYM":"NYN",
                 "NYY":"NYA",
                 "SDP":"SDN",
                 "SFG":"SFN",
                 "STL":"SLN",
                 "TBR":"TBA",
                 "WSN":"WAS",
                 "LAA":"ANA"}
    battingNames = {"ATL":"AtlantaBravesbatting",
                    "ARI":"ArizonaDiamondbacksbatting",
                    "BAL":"BaltimoreOriolesbatting",
                    "BOS":"BostonRedSoxbatting",
                    "CHC":"ChicagoCubsbatting",
                    "CHW":"ChicagoWhiteSoxbatting",
                    "CIN":"CincinnatiRedsbatting",
                    "CLE":"ClevelandIndiansbatting",
                    "COL":"ColoradoRockiesbatting",
                    "DET":"DetroitTigersbatting",
                    "KCR":"KansasCityRoyalsbatting", 
                    "HOU":"HoustonAstrosbatting",
                    "LAA":"AnaheimAngelsbatting",
                    "LAD":"LosAngelesDodgersbatting",
                    "MIA":"MiamiMarlinsbatting",
                    "MIL":"MilwaukeeBrewersbatting",
                    "MIN":"MinnesotaTwinsbatting",
                    "NYM":"NewYorkMetsbatting",
                    "NYY":"NewYorkYankeesbatting",
                    "OAK":"OaklandAthleticsbatting",
                    "PHI":"PhiladelphiaPhilliesbatting",
                    "PIT":"PittsburghPiratesbatting",
                    "SDP":"SanDiegoPadresbatting", 
                    "SEA":"SeattleMarinersbatting", 
                    "SFG":"SanFranciscoGiantsbatting",
                    "STL":"StLouisCardinalsbatting", 
                    "TBR":"TampaBayRaysbatting", 
                    "TEX":"TexasRangersbatting", 
                    "TOR":"TorontoBlueJaysbatting", 
                    "WSN":"WashingtonNationalsbatting"} 
    date = gameInfo["Date"]
    home = gameInfo["HomeGame"]
    if home == 0:
        opp = gameInfo["Opp"]
        if opp in teamNames:
            opp = teamNames[opp]
        url = "http://www.baseball-reference.com/boxes/" + opp + "/" + opp + str(date) + ".shtml"
    else:
        team = gameInfo["Team"]
        if team in teamNames:
            team = teamNames[team]
        url = "http://www.baseball-reference.com/boxes/" + team + "/" + team + str(date) + ".shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    battingInfo = battingNames[gameInfo["Team"]]
    tables = soup.findAll('table', id = battingInfo)
    data_rows = tables[0].findAll('tr')  
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))
        ]
    data = pandas.DataFrame(game_data)
    data = data[data[0].notnull()]
    data = data.reset_index(drop = True)
    data.rename(columns = {0 :"Name", 1 :"AB", 2 :"R",
                               3 :"H", 4 :"RBI", 5:"BB", 6:"SO", 7:"PA",
                              8:"batting_avg", 9:"onbase_perc", 10:"sluggin_perc", 11:"ops", 12:"pitches", 13:"strikes_total",
                              14:"wba_bat", 15:"ali", 16:"WPAplus", 17:"WPAminus", 18:"re24_bat", 19:"PO",
                              20:"A", 21:"details"}, inplace = True)
    names = []
    for i in data["Name"]:
        if len(i) > 0:
            xx = (i.split(" ")[0] + "_" + i.split(" ")[1])
            xx = xx.replace("\xa0", "")
            names.append(xx)
        else:
            names.append("NA")
    data["Name"] = names
    data["Date"] = date
    data["HomeGame"] = home
    data = data[data.Name != "NA"]
    for d in data:
        if d not in ["Name", "details", "Date", "HomeGame"]:
            tmp = Quantify(data[d])
            data[d] = tmp 
    data = data[data["AB"] > 0]
    return(data)
    
def wrapper (team, year, overwrite = True):
    directory = ("data/BoxScores/" + str(year) + "/") 
    if not os.path.exists(directory):
        os.makedirs(directory)       
    if overwrite == False:
        if os.path.exists(directory + team + ".csv"):
            return("This already exists!")
    dat = finder(team, year)
    DatDict = dict()
    for r in range(len(dat)):
        inputs = dat.loc[r]
        try:
            DatDict[r] = GameFinder(inputs)            
        except IndexError:
            pass
    playerGameData = pandas.concat(DatDict) 
    playerGameData.to_csv(directory + team + ".csv")

#teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL',
#         'DET', 'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY',
#         'OAK', 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR',
#         'WSN'] 

#years = [2016]

#for y in years:
#    for t in teams:
#        try:
#            wrapper(t, y, overwrite = True)            
#        except KeyError:    
#            pass
        
wrapper(team, year, overwrite = True)
    
