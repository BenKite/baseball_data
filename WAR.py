## Ben Kite
## 2017-01-14

import pandas, numpy, requests, bs4, scipy.stats.stats, os
import statsmodels.api as sm
import matplotlib.pyplot as plt

from matplotlib._png import read_png
from matplotlib.cbook import get_sample_data
from matplotlib.offsetbox import TextArea, DrawingArea, OffsetImage, AnnotationBbox

datdir = "data/"

teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 
         'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 
         'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

def WARdat (year):
    batdict = dict()
    pdict = dict()

    for t in teams:
        batdict[t] = pandas.read_csv(datdir + t + "_" + str(year) + "_Valuebatting.csv")
        pdict[t] = pandas.read_csv(datdir + t + "_" + str(year) + "_Valuepitching.csv")
    
    batdat = pandas.concat(batdict)
    pdat = pandas.concat(pdict)
    
    batdat = batdat.reset_index(drop = True)
    pdat = pdat.reset_index(drop = True)
    return(batdat, pdat)

bdat16, pdat16 = WARdat(2016)
bdat15, pdat15 = WARdat(2015)

def WARAdd(currentyear, previousyear):
    unadjustedWAR = []
    for row in range(0, len(currentyear)):
        player = currentyear.loc[row]["Name"]
        previous = previousyear[previousyear["Name"] == player]
        unadjustedWAR.append(numpy.sum(previous["WAR"]))
    
    currentyear["PWAR"] = unadjustedWAR
    return(currentyear)
    
bdat16 = WARAdd(bdat16, bdat15)
pdat16 = WARAdd(pdat16, pdat15)

batting = bdat16[["Name", "Team", "Year", "WAR", "PWAR"]]
pitching = pdat16[["Name", "Team", "Year", "WAR", "PWAR"]]

combined = pandas.concat([batting, pitching])
out = combined[combined["Name"] != "Team_Total"]
out = out.sort_values(by = "Team")
playerdat = out.reset_index(drop = True)

teamdat = dict()

for t in teams:
    tmp = playerdat[playerdat["Team"] == t]
    xx = numpy.sum(tmp["WAR"])
    yy = numpy.sum(tmp["PWAR"])
    teamdat[t] = pandas.DataFrame({"Team": t, "WAR": xx, "PWAR": yy}, index = range(0, 1))

teamdat = pandas.concat(teamdat)
teamdat = teamdat.reset_index(drop = True)

def recordGraber(league, year):
    url = "http://www.baseball-reference.com/leagues/" + league + "/" + str(year) + ".shtml"
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text)
    datadict = dict()
    divisions = ["E", "C", "W"]
    for d in divisions:
        tableid = "standings_" + d
        table = soup.findAll('table', id = tableid)
        data_rows = table[0].findAll('tr')  
        game_data = [[td.getText() for td in data_rows[i].findAll('td')]
            for i in range(len(data_rows))
            ]
        datadict[d] = pandas.DataFrame(game_data)
    leagueData = pandas.concat(datadict)
    
    leagueData.rename(columns = {0 :"LongTeam", 1 :"Team", 2 :"Wins",
                              3 :"Losses", 4 :"WinPercentage", 5:"GB"}, inplace = True)
    
    leagueData = leagueData[leagueData.Team.notnull()]
    data = leagueData.reset_index(drop = True)
    return(data)
    
alrec = recordGraber("AL", 2016)
nlrec = recordGraber("NL", 2016)

rec = pandas.concat([alrec, nlrec])
wardat = pandas.merge(teamdat, rec, how = "left", on = "Team")
wardat["Wins"] = pandas.to_numeric(wardat["Wins"])

wardat["PWAR"] = wardat["PWAR"] * numpy.sum(wardat["WAR"])/numpy.sum(wardat["PWAR"])

wardat["Int"] = 1
wardat["PWins"] = wardat["PWAR"] + 47

preds = ["Int", "PWins"]
est = sm.OLS(wardat["Wins"], wardat[preds])
est = est.fit()
est.summary()
       
outdat = wardat[["Team", "WAR", "Wins", "PWAR", "PWins"]]
outdat.to_excel("WAR.xlsx", index = False)

wardat["Differential"] = wardat["Wins"] - wardat["PWins"] 

## Plot the prediction

fig, ax = plt.subplots(figsize = (15, 15))
ax.scatter(wardat["PWins"], wardat["Wins"])

plt.plot(wardat["PWins"], wardat["Wins"], "o")
plt.plot(wardat["PWins"], 1*wardat["PWins"] + 0, "-")
plt.xlabel("Predicted Wins", fontsize = 20)
plt.ylabel("Wins", fontsize = 20)

plt.tick_params(labelsize = 20)
ateams = ["CIN", "SDP", "ATL", "LAA", "CHW", "PIT", "NYM", "SFG", "TBR"]

location = {"CIN": (55, 65),
            "SDP": (65, 68),
            "ATL": (60, 65),
            "LAA": (75, 72),
            "CHW": (76, 80),
            "PIT": (82, 78),
            "NYM": (90, 82),
            "SFG": (92, 85),
            "TBR": (88, 65)}

for t in teams:
    tmp = wardat[wardat["Team"] == t]
    if t not in ateams:
        ax.annotate(t,(tmp["PWins"],tmp["Wins"]), size = 15)
        fn = "teamlogos/" + t + ".png"
        #if os.path.isfile(fn):
        #    arr_lena = read_png(fn)
        #    imagebox = OffsetImage(arr_lena, zoom=0.2)
        #   ab = AnnotationBbox(imagebox, xy = (tmp["PWins"], tmp["Wins"]),
        #            xybox=(0, 0),
        #            xycoords='data',
        #            boxcoords="offset points",
        #            pad=0, frameon = False
        #            )
        #    ax.add_artist(ab)
        # else:
        ax.annotate(t,(tmp["PWins"],tmp["Wins"]), size = 15)
    else:
        ax.annotate(t,(tmp["PWins"],tmp["Wins"]), size = 15, xytext=location[t],
            arrowprops=dict(facecolor='black', shrink=0.01))
     
fig.savefig("plot.png", dpi=fig.dpi)
    
    