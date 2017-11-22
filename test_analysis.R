library(readr)
library(Hmisc)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
cnames = c("iati_version","transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type")
flat <- read_csv("flat.csv",col_names=cnames)

# describe(flat)

flat <- subset(flat,value>0)
flat$year <- substr(flat$value_date,1,4)

short_sec = unique(flat$sector)[which(nchar(unique(flat$sector))<=5 & unique(flat$sector)!="Other")]
short_country <- unique(flat$recipient_country)[which(nchar(unique(flat$recipient_country))<=2)]
short_country <- unique(c(short_country,c(0:9999)))
uncoded <- list(
  "transaction_type" = c("3","IF","D","C","E","4","2","1","I","2005-03-31","if")
  ,"currency" = c(as.character(0:999))
  ,"sector" = short_sec
  ,"recipient_country" = short_country
  # ,"recipient_region"
  # ,"flow_type_code"
  # ,"disbursement_channel"
  # ,"finance_type"
  # ,"aid_type_code"
)
flat_valid = flat
for(code in names(uncoded)){
  message(code)
  flat_valid = subset(flat_valid,!(get(code) %in% uncoded[[code]] ))
}

flat2017 <- subset(flat,year==2017)
flat_valid2017 <- subset(flat_valid,year==2017)

message("Total value for 2017: ",format(sum(flat2017$value,na.rm=TRUE),big.mark=",",scientific=FALSE))
message("Total valid value for 2017: ",format(sum(flat_valid2017$value,na.rm=TRUE),big.mark=",",scientific=FALSE))

message("Lost value if we toss out codes: ",format(sum(flat2017$value,na.rm=TRUE)-sum(flat_valid2017$value,na.rm=TRUE),big.mark=",",scientific=FALSE))

describe(flat_valid)
