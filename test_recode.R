library(readr)
library(Hmisc)

wd <- "C:/Users/Alex/Documents/Data/IATI/"
setwd(wd)
cnames = c("iati_version","transaction_type","transaction_date","currency","value","value_date","provider_org_ref","provider_org_text","provider_org_type","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type")
flat <- read_csv("flat_25k.csv",col_names=cnames)

oda <- subset(flat,value>0)

# The ODA aid bundle is derived from the OECD CRS data set (https://stats.oecd.org/DownloadFiles.aspx?DatasetCode=CRS1) using 15 of its columns.
# Only CRS records (rows) that pertain to ODA are used.
# A CRS record (row) is defined as pertaining to ODA if "category" = 10 and flow_code is one of (11, 12, 13, 19) where:
#   
#   flow_code |                flow_name
# ---------------+------------------------------------------
#   11 | ODA Grants
# 12 | ODA Grant-Like
# 13 | ODA Loans
# 19 | Equity Investment
oda <- subset(oda,flow_type_code==10)
# 
# In the context of OOFs, the ODA aid bundle rules do not apply.
# The ODA aid bundle rules were created by Rob Tew and use the following CRS columns:
#   
#   1) year (SMALLINT)
oda$year <- substr(oda$value_date,1,4)
# 2) donor_code (SMALLINT)
oda$donor_code <- oda$provider_org_ref
oda <- subset(oda,!is.na(provider_org_ref))
# 3) recipient_code (SMALLINT)
oda$recipient_code <- oda$recipient_country
oda <- subset(oda,!is.na(recipient_country))
# 4) flow_code (SMALLINT): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, "Type of flow" tab
oda$flow_code = oda$flow_type_code
# 5) category (SMALLINT): there are currently, as of 2017/06/25 release, 4 categories (with no descriptions available) in the CRS. They are:
oda$category <- NA
#   
#   category
# ----------
#   10
# 20
# 30
# 35
# (4 rows)
# 
# If you need more info, please let me know.
# 
# 6) finance_type (SMALLINT): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, "Type of finance" tab
oda <- subset(oda,!is.na(finance_type))
# 7) aid_type (CHARACTER VARYING): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, "Type of aid" tab
oda$aid_type <- oda$aid_type_code
oda <- subset(oda,!is.na(aid_type))
# 8) usd_disbursement (NUMERIC) 10^6 USD
#This sample is just EUR
x_rates = data.frame(year=c(2006,2007,2009:2016),usdpereur=c(1.26,1.37,1.39,1.33,1.39,1.28,1.33,1.33,1.11,1.11))
oda <- merge(oda,x_rates,all.x=TRUE,by="year")
if(sum(!(oda$currency == "EUR"))==0){
  oda$usd_disbursement = oda$value * oda$usdpereur
}
# 9) short_description (TEXT)
oda$short_description = NA
# 10) purpose_code (INTEGER): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, referred to as "CRS code" in "Purpose code" tab. In theory, only 5 digit codes should be provided here by the data supplier. In reality, some suppliers enter a 3 digit code which is technically the sector code (see below) or the "DAC 5" code.
oda$purpose_code = NA
# 11) sector_code (INTEGER): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, referred to as "DAC 5" code in "Purpose code" tab.
oda$sector_code = oda$sector
oda <- subset(oda,!is.na(sector_code))
# 12) channel_code (INTEGER): details in OECD DAC & CRS LoC http://www.oecd.org/dac/stats/documentupload/DAC-CRS-CODES.xls, "Channel code" tab.
oda$channel_code = oda$disbursement_channel
oda <- subset(oda,!is.na(channel_code))
# 13) long_description (TEXT)
oda$long_description <- NA
# 14) ftc (SMALLINT): free-standing technical co-operation, details in https://www.oecd.org/dac/stats/documentupload/DCDDAC(2016)3FINAL.pdf,
# page 44.
oda$ftc <- NA
# 15) pba (SMALLINT): programme-based approaches, details is https://www.oecd.org/dac/stats/documentupload/DCDDAC(2016)3FINAL.pdf,
# page 43.
oda$pba <- NA

keep <- c("year","donor_code","recipient_code","flow_code","category"
          ,"finance_type","aid_type","usd_disbursement","short_description","purpose_code"
          ,"sector_code","channel_code","long_description","ftc","pba"
          )
oda <- oda[keep]
