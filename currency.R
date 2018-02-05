library(data.table)
library(reshape2)
library(readr)

setwd("/git/iati_flat_testing")

dat <- read_delim("weo_currency.csv",delim="\t",na=c("","n/a","--"))

mdat <- melt(dat,id.vars=c("ISO","Country","Units"),measure.vars=c(7:49),variable.name="year")
mdat <- mdat[complete.cases(mdat),]
wdat <- dcast(mdat,ISO+Country+year~Units)
names(wdat) <- make.names(names(wdat))
wdat$ex.rate <- wdat$U.S..dollars/wdat$National.currency

ex.string <- function(country){
  ctry <- subset(wdat,Country==country)
  ctry <- ctry[order(ctry$year),]
  ctry$string <- paste(ctry$year,ctry$ex.rate,sep=":")
  return(paste(ctry$string,collapse=","))
}
