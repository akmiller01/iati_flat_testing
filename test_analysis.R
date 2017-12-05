library(readr)
library(Hmisc)
library(data.table)
library(openxlsx)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
iati <- read_csv("iati.csv")

iati <- subset(iati,
  (transaction_type_code %in% c("E","D",3,4)) & 
  (sector_vocabulary %in% c(NA,"",1,2,"DAC","DAC-3"))
)


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

fco <- subset(iati,currency!="GBP" & publisher=="fco")
write.csv(fco,"fco_currency.csv",row.names=FALSE,na="")

uni_recip <- data.table(iati)[,.(count=sum(!is.na(iati_identifier))),by=.(publisher,recipient_country_code)]
write.csv(uni_recip,"recip_pub_tab.csv",row.names=FALSE,na="")
