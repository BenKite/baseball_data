#!/usr/bin/env python3

## Ben Kite
## 2017-02-16

"""

Pulls data about players on a given team for a given year.

This pulls out five different tables that are found on
baseball-reference.com: 1) batting, 2) pitching, 3) fielding, 4) value
batting, and 5) value pitching. Saves each table in its own .csv file. 
Names for the output files list the team, the year, and then the table type.


"""

import pandas, os, argparse
import baseballReferenceScrape

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--year", help="Year of games to be collected. Now multiple years can be requested by separating them with a dash(-).  For example '2012-2015'.")
parser.add_argument("--team", help="Name of team you want data for. Defaults to pull for all teams.", default = "ALL")
parser.add_argument("--datdir", help="Name of directory where the data should be stored.  If the directory does not exist it will be created. Defaults to data/", default = "data/")

args = parser.parse_args()

year  = str(args.year)
team = str(args.team)
directory = str(args.datdir)

if not os.path.exists(directory):
    os.makedirs(directory)

if team == "ALL":
    teams = ['ATL', 'ARI', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET',
             'KCR', 'HOU', 'LAA', 'LAD', 'MIA', 'MIL', 'MIN', 'NYM', 'NYY', 'OAK',
             'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN'] 
    checkold = True   
    oldteams = ['ANA', 'BRO', 'CAL', 'FLA', 'KCA', 'MLN', 'MON', 'NYG', 'SLB', 'TBD', 'WSA']
    
else:
    teams = [team]
    checkold = False

## Now a range of years is supported
ys= year.split("-")
if len(ys) > 1:
    ys = range(int(ys[0]), int(ys[1]) + 1)
years = []
for y in ys: years.append(str(y))
 
for year in years:      
    for t in teams:
        try:
            Batting = baseballReferenceScrape.pullPlayerData(t, year, "team_batting")
            Batting.to_csv(directory + "/" + t + "_" + str(year) + "_batting.csv", index = False, encoding = "utf-8")
        except IndexError:
            pass
    
        try:
            Pitching = baseballReferenceScrape.pullPlayerData(t, year, "team_pitching")
            Pitching.to_csv(directory + "/" + t + "_" + str(year) + "_pitching.csv", index = False, encoding = "utf-8")
        except IndexError:
            pass
    
        try:        
            Fielding =baseballReferenceScrape.pullPlayerData(t, year, "standard_fielding")
            Fielding.to_csv(directory + "/" + t + "_" + str(year) + "_fielding.csv", index = False, encoding = "utf-8")
        except IndexError:
            pass
        
        try:        
            ValueBatting = baseballReferenceScrape.pullPlayerData(t, year, "players_value_batting")
            ValueBatting.to_csv(directory + "/" + t + "_" + str(year) + "_Valuebatting.csv", index = False, encoding = "utf-8")
        except IndexError:
            pass
    
        try:
            ValuePitching = baseballReferenceScrape.pullPlayerData(t, year, "players_value_pitching")
            ValuePitching.to_csv(directory + "/" + t + "_" + str(year) + "_Valuepitching.csv", index = False, encoding = "utf-8")
        except IndexError:
            pass

if checkold:
    for year in years:      
        for t in oldteams:
            try:
                Batting = baseballReferenceScrape.pullPlayerData(t, year, "team_batting")
                Batting.to_csv(directory + "/" + t + "_" + str(year) + "_batting.csv", index = False, encoding = "utf-8")
            except IndexError:
                pass
                
            try:
                Pitching = baseballReferenceScrape.pullPlayerData(t, year, "team_pitching")
                Pitching.to_csv(directory + "/" + t + "_" + str(year) + "_pitching.csv", index = False, encoding = "utf-8")
            except IndexError:
                pass
                
            try:        
                Fielding = baseballReferenceScrape.pullPlayerData(t, year, "standard_fielding")
                Fielding.to_csv(directory + "/" + t + "_" + str(year) + "_fielding.csv", index = False, encoding = "utf-8")
            except IndexError:
                pass
                
            try:        
                ValueBatting = baseballReferenceScrape.pullPlayerData(t, year, "players_value_batting")
                ValueBatting.to_csv(directory + "/" + t + "_" + str(year) + "_Valuebatting.csv", index = False, encoding = "utf-8")
            except IndexError:
                pass
                
            try:
                ValuePitching = baseballReferenceScrape.pullPlayerData(t, year, "players_value_pitching")
                ValuePitching.to_csv(directory + "/" + t + "_" + str(year) + "_Valuepitching.csv", index = False, encoding = "utf-8")
            except IndexError:
                pass

