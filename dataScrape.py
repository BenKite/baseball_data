## Ben Kite
## 2017-01-20

import pandas, numpy
import requests, bs4
import re, os

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
    ## I will update this soon to pull the names from the site!
    ## This was a lazy way to get names at first
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
        

    
