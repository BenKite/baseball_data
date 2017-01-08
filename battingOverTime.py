## Ben Kite
## 2016-04-22

import pandas, os, numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

dat = pandas.read_csv("data/BoxScores/2016/KCR.csv")

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
    return(avgs)   
    
pdat = dat[dat.Name == "Eric_Hosmer"]
pdat.reset_index(inplace = True)

avgs = battAvg(pdat, 5)

def autoregression(avgs, lag):
    x = avgs[lag:len(avgs) - lag]
    A = numpy.vstack([x, numpy.ones(len(x))]).T
    y = avgs[2*lag:]
    coef = numpy.linalg.lstsq(A, y)[0]
    return(coef)

def playerAutoReg(player, dat, gamelag):
    pdat = dat[dat.Name == player]
    pdat.reset_index(inplace = True)
    if numpy.sum(pdat["AB"]) > 100:
        avg = battAvg(pdat, gamelag)    
        reg = autoregression(avg, gamelag)
        return(reg)
    else:
        return([0, 0])

players = numpy.unique(dat["Name"])

gamelag = 5
pcors = dict()        
for p in players:
    tmp = playerAutoReg(p, dat, gamelag)
    tmpdat = []
    if numpy.isnan(tmp[1]) == False:
        tmpdat = {"Intercept": tmp[0], "Slope": tmp[1]}
        outdat = pandas.DataFrame(data = tmpdat, index = [p])
    pcors[p] = (outdat)
        
pcors = pandas.concat(pcors)

## Now I need scatter plots

def autoScatter(avgs, lag, player):
    x = avgs[lag:len(avgs) - lag]
    y = avgs[2*lag:]
    plt.scatter(x, y)
    plt.title(player)
    
def playerAutoScatter(player, dat, gamelag):
    pdat = dat[dat.Name == player]
    pdat.reset_index(inplace = True)
    if numpy.sum(pdat["AB"]) > 100:
        avg = battAvg(pdat, gamelag)    
        autoScatter(avg, gamelag, player)
    else:
        return(0)
   
pp = PdfPages('Royals_AutoScatter_2016.pdf')
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
        line1, = plt.plot(battAvg(pdat, 5), color = 'r', label = "Five Games")
        line2, = plt.plot(battAvg(pdat, 10), color = 'b', label = "Ten Games")
        plt.title(player)
        plt.ylim(0, 1)
        plt.legend(handles = [line1, line2])
    else:
        return(0)        

players = numpy.unique(dat["Name"])

pp = PdfPages('Royals_2016.pdf')
for p in players:
    tmpfig = playerPlotter(p, dat, 150)
    if tmpfig != 0:
        pp.savefig()
pp.close()
    
    
    
