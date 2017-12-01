library(readr)
library(Hmisc)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
iati <- read_csv("iati.csv")

iati <- subset(iati,value>0)

describe(iati)
