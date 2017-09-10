
## Ben Kite
## 2017-01-15

## Batters first
dat <- read.csv("rankings.csv")


library(xtable)

names(dat)[4] <- "Plate\nAppearances"
names(dat)[5] <- "Cumulative\nWPA"

topBat <- xtable(dat[1:15,],  include.rownames = FALSE, align = rep("p{4cm}", 6))
#print(xtab, type = "html", file = "topBatters.txt", include.rownames = FALSE)

botBat <- xtable(dat[(nrow(dat) - 14):nrow(dat),],  include.rownames = FALSE, align = rep("p{4cm}", 6))
#print(xtab, type = "html", file = "bottomBatters.txt", include.rownames = FALSE)

pdat <- read.csv("rankings_pitching.csv")

names(pdat)[5] <- "Cumulative\nWPA"

topPitch <- xtable(pdat[1:15,],  include.rownames = FALSE, align = rep("p{4cm}", 6))
#print(xtab, type = "html", file = "topPitchers.txt", include.rownames = FALSE)

botPitch <- xtable(pdat[(nrow(pdat) - 14):nrow(pdat),],  include.rownames = FALSE, align = rep("p{4cm}", 6))
#print(xtab, type = "html", file = "bottomPitchers.txt", include.rownames = FALSE)

Webpage <- "
<h3>Win Probability Added by Batters (updated DATE)</h3>
<h4>Top 15 Players</h4>
TOPBATTERS
<h4>Bottom 15 Players</h4>
BOTTOMBATTERS
<h3>Win Probability Added by Pitchers (updated DATE)</h3>
<h4>Top 15 Pitchers </h4>
TOPPITCHERS
<h4>Bottom 15 Pitchers </h4>
BOTTOMPITCHERS
"
Webpage <- gsub("DATE", Sys.Date(), Webpage)
Webpage <- gsub("TOPBATTERS", print(topBat, type = "html", include.rownames = FALSE), Webpage)
Webpage <- gsub("BOTTOMBATTERS", print(botBat, type = "html", include.rownames = FALSE), Webpage)
Webpage <- gsub("TOPPITCHERS", print(topPitch, type = "html", include.rownames = FALSE), Webpage)
Webpage <- gsub("BOTTOMPITCHERS", print(botPitch, type = "html", include.rownames = FALSE), Webpage)

cat(Webpage, file = "pastetosite.txt")

