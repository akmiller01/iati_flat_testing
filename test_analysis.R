library(readr)
library(Hmisc)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
cnames = c("iati_version","transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type")
flat <- read_csv("flat.csv",col_names=cnames)

describe(flat)
