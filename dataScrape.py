## Ben Kite
## 2016-04-22

import pandas, numpy
import requests, bs4
import re

def finder (team, year):
    url = "http://www.baseball-reference.com/teams/" + team + "/" + str(year) + "-schedule-scores.shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    tables = soup.findAll('table', id = "team_schedule")
    data_rows = tables[0].findAll('tr')  
    game_data = [[td.getText() for td in data_rows[i].findAll('td')]
        for i in range(len(data_rows))
        ]
    dat = pandas.DataFrame(game_data)
    dat = dat[dat[0].notnull()]
    dat = dat.reset_index(drop = True)
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
    
def playerdata (team, year, tabletype):
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
    

  
    
    



