library(readr)
library(Hmisc)
library(data.table)
library(openxlsx)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
# iati_unsplit <- read_csv("iati_unsplit.csv")
# 
# iati_unsplit <- subset(iati_unsplit,
#   (!is.na(sector_code))
#   & (!is.na(recipient_code))
# )
# 
# iati_unsplit_sum <- sum(iati_unsplit$value,na.rm=TRUE)

iati <- read_csv("iati.csv")

iati <- subset(iati,
  (!is.na(sector_code))
  & (!is.na(recipient_code))
)

# iati_sum <- sum(iati$value,na.rm=TRUE)
# 
# diff <- iati_unsplit_sum - iati_sum
# 
# perc.diff <- (diff/iati_unsplit_sum)*100
# message(perc.diff)

setwd("C:/git/iati_flat_testing/output/")

wb <- createWorkbook()

for(varname in names(iati)){
  if(varname!="category"){
    if(nrow(unique(iati[,varname]))<1000){
      message(varname)
      df <- data.frame(table(iati[,varname],useNA="ifany"))
      total <- sum(df$Freq)
      df <- transform(df,Perc=Freq/total)
      setnames(df,"Var1",varname)
      addWorksheet(wb,varname)
      writeDataTable(wb,varname,df)
    }
  }
}

saveWorkbook(wb,file="iati_freq.xlsx",overwrite=TRUE)

rand.samp <- data.table(iati)[sample(.N,5000)]
write.csv(rand.samp,"sample5000.csv",row.names=FALSE,na="")

uni_recip <- data.table(iati)[,.(count=sum(!is.na(iati_identifier))),by=.(publisher,recipient_code)]
write.csv(uni_recip,"recip_pub_tab.csv",row.names=FALSE,na="")

sink("iati_sumstats.txt")
describe(iati)
closeAllConnections() 