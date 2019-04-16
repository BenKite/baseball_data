## Ben Kite

import pandas, numpy
import requests, bs4
import re, os
import baseballReferenceScrape as ds
import matplotlib.pyplot as plt
from pylab import *

def wpaer (pitcher, bdat):
    duck = []
    for duckinga in bdat["Pitcher"]:
        duck.append(duckinga.replace("\xa0", "_"))
    bdat["Pitcher"] = duck
    dat = bdat.loc[bdat["Pitcher"]== pitcher]
    dat = dat.reset_index()
    #wwpa = dat["wWPA"]
    #vals = []
    #for w in wwpa:
    #    tmp = w.split("%")[0]
    #    vals.append(tmp)
    #vals = pandas.to_numeric(vals)
    winprob = []
    vals = []
    for rown in range(0, len(dat)):
        row = dat.loc[rown]
        if row["wWPA"] == row["wWPA"]:
            if row["Pteam"] == row["Winner"]:
                winprob.append(1)
            else: 
                winprob.append(-1)
            w = row["wWPA"]
            tmp = w.split("%")[0]
            vals.append(tmp)
    vals = pandas.to_numeric(vals)
    vals = vals * winprob
    return(vals)


## All teams and batters
teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 
         'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 
         'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

year = 2019

## This takes a while to run the first time.
teamdat = dict()
for t in teams:
    filen = t + "_pbp_" + str(year) + ".csv"
    if os.path.isfile(filen):
        teamdat[t] = pandas.read_csv(filen)
        teamdat[t]["batteam"] = t
    else:
        ds.pullPlaybyPlay(t, year, filen)
        teamdat[t] = pandas.read_csv(filen)
        teamdat[t]["batteam"] = t
    
tdat = pandas.concat(teamdat)
tdat = tdat.reset_index()

apitchers = numpy.unique(tdat["Pitcher"])

teamPitching = dict()
for t in teams:
    teamdat = tdat.loc[(tdat["Pteam"] == t)]
    tpitchers = numpy.unique(teamdat["Pitcher"])
    out = dict()
    for a in tpitchers:
        a = a.replace("\xa0", "_")
        aa = wpaer(a, teamdat)
        out[a] = pandas.DataFrame({"Name": a, "Team": t, "Batters Faced": len(aa), "Cumulative wWPA": numpy.sum(aa)/100}, index = [a])
    bb = pandas.concat(out)
    teamPitching[t] = bb.reset_index(drop = True)

output = pandas.concat(teamPitching)  

output = output.sort_values("Cumulative wWPA", ascending = False)

output = output.reset_index(drop = True)
output["Rank"] = output.index + 1

output = output[["Rank", "Name", "Team", "Batters Faced", "Cumulative wWPA"]]
cleannames = []
for n in output["Name"]:
    cleannames.append(re.sub("_", " ", n))
    
output["Name"] = cleannames
output.to_csv("rankings_pitching.csv", index = False)  
    
def render_mpl_table(data, col_width=3.0, row_height=0.625, font_size=14,
                         header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',
                         bbox=[0, 0, 1, 1], header_columns=0,
                         ax=None, **kwargs):
    if ax is None:
        size = (numpy.array(data.shape[::-1]) + numpy.array([0, 1])) * numpy.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)

    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors) ])
    return ax
    
render_mpl_table(output.loc[0:14], header_columns=0, col_width=3.2)
savefig("topWWPA_pitching.png", bbox_inches= 'tight')

render_mpl_table(output.loc[len(output) - 15:], header_columns=0, col_width=3.2)
savefig("bottomWWPA_pitching.png", bbox_inches= 'tight')


