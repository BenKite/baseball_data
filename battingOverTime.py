#!/usr/bin/env python3

## Ben Kite
## 2016-04-22

## I was interested in how a player's batting performance changes over
## the course of a season. People like to talk about a batter being
## hot or being in a slump, so I wanted to show the ups and down of a
## player over the course of the season.

## Here I looked at the Royals in the 2016 season while considering
## players with over 100 at bats. I looked at their games in chunks of
## 5 or 10 and computed their batting average just over those games.
## The chunks here overlap, so with 5 game chunks the first is games
## 1-5, whereas the second is 2-6, etc.  I looked at how adjacent
## chunks (e.g., games 1-5 and games 6-10) were related in terms of
## performance with batting average.

## This requires the 2016 data from the Royals that can be obtained by
## running boxScores.py:
## $ python boxScores.py --team KCR --year 2016

## Running this script will produce a pdf with plots showing BA
## trends, as well as a pdf showing the relationship between adjacent
## game chunks.

import pandas, os, numpy, argparse
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from sklearn import datasets, linear_model

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--team", help="Name of team from which you want to collect data.")
parser.add_argument("--year", help="Year of games to be collected")

args = parser.parse_args()

year  = str(args.year)
team = str(args.team)

dat = pandas.read_csv("data/BoxScores/" + str(year) +  "/" + team + ".csv")

def battAvg(pdat, gamesInChunk):
    games = len(pdat)
    avgs = []
    for g in range(0,games):
        if g < gamesInChunk:
            start = 0
        else:
            start = g - gamesInChunk
        xx = pdat.loc[start:g]
        avgs.append(numpy.sum(xx.H) / numpy.sum(xx.AB))
    out = pandas.DataFrame({"Game": pdat["Game"]+ 1, "Average": avgs})
    return(out)   
    
## Now I need scatter plots

def autoScatter(avgs, lag, player):
    avgs = avgs["Average"]
    x = avgs[lag:len(avgs) - lag]
    y = avgs[2*lag:]
    plt.scatter(x, y)
    plt.title(player.replace("_", " "))
    plt.xlabel("Previous Five Games BA")
    plt.ylabel("Next Five Games BA")
    
def playerAutoScatter(player, dat, gamelag):
    pdat = dat[dat.Name == player]
    pdat.reset_index(inplace = True)
    if numpy.sum(pdat["AB"]) > 100:
        avg = battAvg(pdat, gamelag)    
        autoScatter(avg, gamelag, player)
    else:
        return(0)

players = numpy.unique(dat["Name"])
players = players[players != "Team_Totals"]
gamelag = 5
    
pp = PdfPages(team + '_AutoScatter_2016.pdf')
for p in players:
    plt.figure()
    tmp = playerAutoScatter(p, dat, gamelag)
    if tmp != 0:
        pp.savefig()
pp.close()

def playerPlotter(player, dat, minab):  
    pdat = dat[dat.Name == player]
    pdat.reset_index(inplace = True)
    if numpy.sum(pdat["AB"]) >= minab:
        plt.figure()
        line1, = plt.plot(battAvg(pdat, 5)["Game"], battAvg(pdat,5)["Average"], color = 'r', label = "Five Game Average")
        line2, = plt.plot(battAvg(pdat, 10)["Game"], battAvg(pdat,10)["Average"], color = 'b', label = "Ten Game Average")
        line3, = plt.plot(battAvg(pdat, len(pdat))["Game"], battAvg(pdat,len(pdat))["Average"], color = 'black', label = "Season Average")
        plt.title(player.replace("_", " "))
        plt.ylim(0, 1)
        plt.xlim(0, 162)
        plt.xlabel("Games")
        plt.ylabel("Batting Average")
        plt.legend(handles = [line1, line2, line3])
    else:
        return(0)        

pp = PdfPages(team + '_2016.pdf')
for p in players:        
    tmpfig = playerPlotter(p, dat, 150)
    if tmpfig != 0:
        pp.savefig()
pp.close()
    
    
    
