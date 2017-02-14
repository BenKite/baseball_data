## Ben Kite
## 2017-01-20

import pandas, numpy
import requests, bs4
import re, os

## Pulls game level data for team and year provided.
## The team provided must be a three-character abbreviation:
## 'ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
## 'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
## 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN'
def pullGameData (team, year):
    url = "http://www.baseball-reference.com/teams/" + team + "/" + str(year) + "-schedule-scores.shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    tables = soup.findAll('table', id = "team_schedule")
    data_rows = tables[0].findAll('tr')  
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))
        ]
    dat = pandas.DataFrame(game_data)
    dat = dat[dat[0].notnull()]
    dat = dat.reset_index(drop = True)
    ## I decided to name these myself to have more control.
    ## This certainly requires me to keep checking to ensure that column names
    ## stay consistent.  I am considering pulling out the names from the page 
    ## and then renaming them just to be safe.
    dat.rename(columns = {0 :"gamenum", 1 :"gamenum2", 2 :"Date",
                              3 :"boxscore", 4 :"Team", 5:"Location", 6:"Opp", 7:"TeamRecord",
                              8:"Runs", 9:"OppRuns", 10:"Inn", 11:"WL", 12:"Rank", 13:"GB",
                              14:"Win", 15:"Loss", 16:"Save", 17:"Time", 18:"DN", 19:"Attendance",
                              20:"Streak"}, inplace = True)
    dates = dat["Date"]
    ndates = []
    for d in dates:
        month = d.split(" ")[1]
        day = d.split(" ")[2]
        day = day.zfill(2)
        mapping = {"Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                   "Sep": "09", "Oct": "10", "Nov":"11"}
        m = mapping[month]
        ndates.append(str(year) + m + day)
    
    uni, counts = numpy.unique(ndates, return_counts = True)

    ndates = []
    for t in range(len(counts)):
        ux = uni[t]
        cx = counts[t]
        if cx == 1:
            ndates.append(ux + "0")
        else:
            for i in range(int(cx)):
                ii = i + 1
                ndates.append(ux + str(ii))     
    dat["Date"] = ndates  
    
    xx = []
    for i in dat["Location"]:
        if i == "@":
            xx.append(0)
        else:
            xx.append(1)

    dat["HomeGame"] = xx
    
    #keep = []
    #for i in dat["Runs"]:
    #    keep.append(len(i) < 3)

    #dat = dat[keep]

    return(dat)

## Pulls data summarizing the season performance of all players on the
## team provided for the given year.
## The table type argument must be one of five possibilities:
## "team_batting"
## "team_pitching"
## "standard_fielding"
## "players_value_batting"
## "players_value_pitching"
def pullPlayerData (team, year, tabletype):
    url = "http://www.baseball-reference.com/teams/" + team + "/" + str(year) + ".shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    tables = soup.findAll('table', id = tabletype)
    data_rows = tables[0].findAll('tr')
    data_header = tables[0].findAll('thead')    
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))
        ]
    header = data_header[0].getText()
    header = header.split("\n")
    for i in range(0, 4):
        header.remove("")  
    data = pandas.DataFrame(game_data)
    data.columns = header
    data = data[data.Name.notnull()]
    data = data.reset_index(drop = True)
    names = data.columns
    for c in range(0, len(names)):
        replacement = []
        if type (data.loc[0][c]) == str:
            k = names[c]
            for i in range(0, len(data[k])):
                p = data.loc[i][c]
                xx = re.sub("[#@*&^%$!]", "", p)
                xx = xx.replace("\xa0", "_")
                xx = xx.replace(" ", "_")
                replacement.append(xx)
            data[k] = replacement
    data["Team"] = team
    data["Year"] = year
    return(data)

## This is used later to append integers to games on the same date to
## separate them.
def Quantify (x):
    out = []
    for i in x:
        if len(i) < 1:
            out.append(None)
        else:
            out.append(float(i))
    return(out)
    
## Pulls box score data from a game provided in the gameInfo input
## This is meant to be run by the pullBoxScores function below.
def gameFinder (gameInfo):
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

## Pulls all of the boxscores for a team in a given year.
## The directory argument is used to specify where to save the .csv
## If overwrite is True, an existing file with the same name will be overwritten.
def pullBoxscores (team, year, directory, overwrite = True):
    if not os.path.exists(directory):
        os.makedirs(directory)       
    if overwrite == False:
        if os.path.exists(directory + team + ".csv"):
            return("This already exists!")
    dat = pullGameData(team, year)
    DatDict = dict()
    for r in range(len(dat)):
        inputs = dat.loc[r]
        try:
            DatDict[r] = gameFinder(inputs)            
        except IndexError:
            pass
    playerGameData = pandas.concat(DatDict) 
    playerGameData.reset_index(inplace = True)
    playerGameData = playerGameData.rename(columns = {"level_0": "Game", "level_1": "BatPos"})
    playerGameData.to_csv(directory + team + "_" + year + ".csv")
        
## This is an internal function to pullPlaybyPlay
def PlayByPlay (gameInfo):
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
    date = gameInfo["Date"]
    home = gameInfo["HomeGame"]
    if home == 0:
        team = gameInfo["Opp"]
        opp = gameInfo["Team"]
        if opp in teamNames:
            opp = teamNames[opp]
    else:
        team = gameInfo["Team"]
        opp = gameInfo["Opp"]
        if team in teamNames:
            team = teamNames[team]
    url = "http://www.baseball-reference.com/boxes/" + team + "/" + team + str(date) + ".shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    tables = soup.findAll('table', id = "play_by_play")
    data_rows = tables[0].findAll('tr')
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
            for i in range(len(data_rows))
            ]
    data_header = tables[0].findAll('thead')    
    header = data_header[0].getText()
    header = header.replace("\n\n", "")   
    header = header.split("\n")        
    dat = pandas.DataFrame(game_data)
    dat.columns = header
    dat = dat.loc[dat["Batter"].notnull()]
    dat = dat.loc[dat["Play Description"].notnull()]
    dat["Date"] = date
    dat["Hteam"] = team
    dat["Ateam"] = opp
    pteam = []
    pteams = numpy.unique(dat["@Bat"])
    for d in dat["@Bat"]:
        if d == pteams[0]:
            pteam.append(pteams[1])
        else:
            pteam.append(pteams[0])
    dat["Pteam"] = pteam
    return(dat)

## Pulls all of the play by play tables for a team for a given year.
## Output is the name of the .csv file you want to save.  I force a
## file to be saved here because the function takes a while to run.
def pullPlaybyPlay (team, year, output):
    oteam = team
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
    dat = pullGameData(team, year)
    if team in teamNames:
        team = teamNames[team]
    DatDict = dict()
    for r in range(len(dat)):
        inputs = dat.loc[r]
        hteam = inputs["Team"]
        ateam = inputs["Opp"]
        if hteam in teamNames:
            inputs["Team"] = teamNames[hteam]
        if ateam in teamNames:
            inputs["Opp"] = teamNames[ateam]
        try:
            DatDict[r] = PlayByPlay(inputs)            
        except IndexError:
            pass
    bdat = pandas.concat(DatDict)
    bdat["Hteam"] = oteam
    names = []
    for i in bdat["Batter"]:
        if len(i) > 0:
            xx = i
            xx = xx.replace("\xa0", "")
            names.append(xx)
        else:
            names.append("NA")
    bdat["BatterName"] = names
    ## These rules attempt to sort out different play outcomes by
    ## searching the text in the "Play Description" variable.
    bdat["out"] = (bdat["Play Description"].str.contains("out")) | (bdat["Play Description"].str.contains("Play")) | (bdat["Play Description"].str.contains("Flyball")) | (bdat["Play Description"].str.contains("Popfly")) 
    bdat["hbp"] = bdat["Play Description"].str.startswith("Hit")
    bdat["walk"] = (bdat["Play Description"].str.contains("Walk"))
    bdat["stolenB"] = bdat["Play Description"].str.contains("Steal")
    bdat["wild"] = bdat["Play Description"].str.startswith("Wild") | bdat["Play Description"].str.contains("Passed")
    bdat["error"] = bdat["Play Description"].str.contains("Reached on")
    bdat["pick"] = bdat["Play Description"].str.contains("Picked")
    bdat["balk"] = bdat["Play Description"].str.contains("Balk")
    bdat["interference"] = bdat["Play Description"].str.contains("Reached on Interference")
    bdat["sacrifice"] = bdat["Play Description"].str.contains("Sacrifice")
    bdat["ab"] = (bdat["walk"] == False) & (bdat["sacrifice"] == False) & (bdat["interference"] == False) & (bdat["stolenB"] == False) & (bdat["wild"] == False) & (bdat["hbp"] == False) & (bdat["pick"] == False) & (bdat["balk"] == False)
    bdat["hit"] =  (bdat["walk"] == False) & (bdat["out"] == False) & (bdat["stolenB"] == False) & (bdat["error"] == False) & (bdat["ab"] == True)
    bdat.to_csv(output)
    return(bdat)

## This pulls information about which hand a pitcher throws with.  I
## made this solely to allow pitcher handedness to be used as a
## variable in models.
def pullPitcherData (team, year):
    url = "http://www.baseball-reference.com/teams/" + team + "/" + str(year) + ".shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    tables = soup.findAll('table', id = "team_pitching")
    data_rows = tables[0].findAll('tr')
    data_header = tables[0].findAll('thead')    
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))
        ]
    header = data_header[0].getText()
    header = header.split("\n")
    for i in range(0, 4):
        header.remove("")  
    data = pandas.DataFrame(game_data)
    data.columns = header
    data = data[data.Name.notnull()]
    data = data[data.Rk.notnull()]
    data = data[data.G != "162"]
    data = data.reset_index(drop = True)
    data["Team"] = team
    data["Year"] = year
    data["LeftHanded"] = data["Name"].str.endswith("*")  
    names = data.columns
    for c in range(0, len(names)):
        replacement = []
        if type (data.loc[0][c]) == str:
            k = names[c]
            for i in range(0, len(data[k])):
                p = data.loc[i][c]
                xx = re.sub("[#@&*^%$!]", "", p)
                xx = xx.replace("\xa0", "_")
                xx = xx.replace(" ", "_")
                replacement.append(xx)
            data[k] = replacement
    data = data[["Name", "LeftHanded", "Team", "Year"]]
    return(data)
    
