## Ben Kite

import pandas, numpy
import requests, bs4
import re, os
import baseballReferenceScrape as ds
import matplotlib.pyplot as plt
from pylab import *


def wpaer (batter, bdat):
    duck = []
    for duckinga in bdat["Batter"]:
        duck.append(duckinga.replace("\xa0", "_"))
    bdat["Batter"] = duck
    dat = bdat.loc[bdat["Batter"]== batter]
    dat.reset_index(inplace = True, drop = True)
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
            if row["@Bat"] == row["Winner"]:
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

## This takes a while to run the first time, but in September of '17 I
## made changes that allow data files to be updated, rather than
## deleting them and starting over each time.
teamdat = dict()
for t in teams:
    filen = t + "_pbp_" + str(year) + ".csv"
    if os.path.isfile(filen):
        teamdat[t] = pandas.read_csv(filen)
        teamdat[t]["batteam"] = t
    else:
        ds.pullPlaybyPlay(t, year, filen, check = False)
    teamdat[t] = pandas.read_csv(filen)
    teamdat[t]["batteam"] = t

    
tdat = pandas.concat(teamdat)
tdat.reset_index(inplace = True, drop = True)

abatters = numpy.unique(tdat["Batter"])

teamBatting = dict()
for t in teams:
    teamdat = tdat.loc[(tdat["batteam"] == t) & (tdat["@Bat"] == t)]
    tbatters = numpy.unique(teamdat["Batter"])
    out = dict()
    for a in tbatters:
        a = a.replace("\xa0", "_")
        aa = wpaer(a, teamdat)
        out[a] = pandas.DataFrame({"Name": a, "Team": t, "Plate Appearances": len(aa), "Cumulative wWPA": numpy.sum(aa)/100}, index = [a])
    bb = pandas.concat(out)
    teamBatting[t] = bb.reset_index(drop = True)

output = pandas.concat(teamBatting)  

output = output.sort_values("Cumulative wWPA", ascending = False)

output = output.reset_index(drop = True)
output["Rank"] = output.index + 1

output = output[["Rank", "Name", "Team", "Plate Appearances", "Cumulative wWPA"]]
cleannames = []
for n in output["Name"]:
    cleannames.append(re.sub("_", " ", n))
    
output["Name"] = cleannames
output.to_csv("rankings.csv", index = False)   
    
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
savefig("topWWPA.png", bbox_inches= 'tight')

render_mpl_table(output.loc[len(output) - 15:], header_columns=0, col_width=3.2)
savefig("bottomWWPA.png", bbox_inches= 'tight')


