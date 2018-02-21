library(data.table)
library(readr)

setwd("C:/Users/Alex/Documents/Data/IATI/")

agg <- read_csv("iati_unfiltered_agg.csv")
dagg <- read_csv("iati_unfiltered_disagg.csv")

transactions.aggregate <- subset(agg,budget_or_transaction=="Transaction")
budgets.aggregate <- subset(agg,budget_or_transaction=="Budget")

transactions.aggregate.2017 <- subset(transactions.aggregate,year==2017)
trans.2017.tab <- data.table(transactions.aggregate.2017)[,.(value=sum(usd_disbursement,na.rm=TRUE)),by=.(publisher,year)]

budgets.aggregate.17.18.19 <- subset(budgets.aggregate,year %in% c(2017,2018,2019))

bud.17.18.19.tab <- data.table(budgets.aggregate.17.18.19)[,.(value=sum(usd_disbursement,na.rm=TRUE)),by=.(publisher,year)]

iati_members <- c(
  "Ghana"
  ,"Liberia"
  ,"Nigeria"
  ,"Rwanda"
  ,"Sierra Leone"
  ,"Somalia"
  ,"Tanzania"
  ,"Malawi"
  ,"Burkina Faso"
  ,"Burundi"
  ,"Madagascar"
  ,"Benin"
  ,"Democratic Republic of the Congo"
  ,"Congo"
  ,"Guinea"
  ,"Mali"
  ,"Bangladesh"
  ,"Indonesia"
  ,"Myanmar"
  ,"Nepal"
  ,"Viet Nam"
  ,"Colombia"
  ,"Honduras"
  ,"Dominican Republic"
  ,"Montenegro"
  ,"Moldova"
  ,"Lebanon"
  ,"Syrian Arab Republic"
  ,"Yemen"
  ,"Papua New Guinea"
)

iati_member_codes <- c(
  # Ghana
  "GH" #ISO2
  ,"GHA" #ISO3
  ,"241" #CRS
  # Liberia
  ,"LR"
  ,"LBR"
  ,"251"
  # Nigeria
  ,"NG"
  ,"NGA"
  ,"261"
  # Rwanda
  ,"RW"
  ,"RWA"
  ,"266"
  # Sierra Leone
  ,"SL"
  ,"SLE"
  ,"272"
  # Somalia
  ,"SO"
  ,"SOM"
  ,"273"
  # Tanzania
  ,"TZ"
  ,"TZA"
  ,"282"
  # Malawi
  ,"MW"
  ,"MWI"
  ,"253"
  # Burkina Faso
  ,"BF"
  ,"BFA"
  ,"287"
  # Burundi
  ,"BI"
  ,"BDI"
  ,"228"
  # Madagascar
  ,"MG"
  ,"MDG"
  ,"252"
  # Benin
  ,"BJ"
  ,"BEN"
  ,"236"
  # Democratic Republic of Congo
  ,"CD"
  ,"COD"
  ,"235"
  # Republic of the Congo
  ,"CG"
  ,"COG"
  ,"234"
  # Guinea
  ,"GN"
  ,"GIN"
  ,"243"
  # Mali
  ,"ML"
  ,"MLI"
  ,"255"
  # Bangladesh (Vice Chair)
  ,"BD"
  ,"BGD"
  ,"666"
  # Indonesia
  ,"ID"
  ,"IDN"
  ,"738"
  # Myanmar
  ,"MM"
  ,"MMR"
  ,"635"
  # Nepal
  ,"NP"
  ,"NPL"
  ,"660"
  # Vietnam
  ,"VN"
  ,"VNM"
  ,"769"
  # Colombia
  ,"CO"
  ,"COL"
  ,"437"
  # Honduras
  ,"HN"
  ,"HND"
  ,"351"
  # Dominican Republic
  ,"DO"
  ,"DOM"
  ,"340"
  # Montenegro
  ,"ME"
  ,"MNE"
  ,"65"
  # Moldova
  ,"MD"
  ,"MDA"
  ,"93"
  # Lebanon
  ,"LB"
  ,"LBN"
  ,"555"
  # Syria
  ,"SY"
  ,"SYR"
  ,"573"
  # Yemen
  ,"YE"
  ,"YEM"
  ,"580"
  # Papua New Guinea
  ,"PG"
  ,"PNG"
  ,"862"
)

recode_iati_members <- function(x){
  return(iati_members[ceiling(which(iati_member_codes==x)/3)])
}

transactions.disaggregate <- subset(dagg,budget_or_transaction=="Transaction")
transactions.disaggregate.15.16.17 <- subset(transactions.disaggregate,year %in% c(2015,2016,2017))

transactions.disaggregate.15.16.17$recipient_code <- toupper(transactions.disaggregate.15.16.17$recipient_code)
transactions.disaggregate.15.16.17 <- subset(transactions.disaggregate.15.16.17,recipient_code %in% iati_member_codes)
transactions.disaggregate.15.16.17$recipient <- sapply(transactions.disaggregate.15.16.17$recipient_code,recode_iati_members)

transactions.disaggregate.15.16.17$publisher[which(transactions.disaggregate.15.16.17$publisher=="usaid")] = "unitedstates"
transactions.disaggregate.15.16.17$publisher[which(transactions.disaggregate.15.16.17$publisher=="ec-echo")] = "ec-devco"
transactions.disaggregate.15.16.17$publisher[which(transactions.disaggregate.15.16.17$publisher=="ec-near")] = "ec-devco"

trans.recip.donor.tab <- data.table(transactions.disaggregate.15.16.17)[,.(value=sum(usd_disbursement,na.rm=TRUE)),by=.(recipient,publisher,year)]

trans.recip.max <- trans.recip.donor.tab[,.(value=max(value)),by=.(recipient,publisher)]

trans.recip.max <- merge(trans.recip.max,trans.recip.donor.tab,all.x=TRUE)
setnames(trans.recip.max,"year","iati.year")
setnames(trans.recip.max,"value","iati.value")

exclude <- c("abt","akfuk73","dec-uk","palladium","plan_usa","spuk","wwf-uk")
trans.recip.max <- subset(trans.recip.max,!(publisher %in% exclude))

crs <- read_csv("crs.csv")

crs <- subset(crs,Recipient %in% iati_members)
crs$Value <- crs$Value*1000000
setnames(crs,"Value","value")
setnames(crs,"Year","year")
setnames(crs,"Recipient","recipient")
setnames(crs,"Donor","donor")
keep <- c("recipient","donor","year","value")
crs <- crs[keep]

vague_donors <- c(
  "All Donors, Total"
  ,"DAC Countries, Total"
  ,"Multilaterals, Total"
  ,"Non-DAC Countries, Total"
  ,"Memo: Private Donors, Total"
  ,"G7 Countries, Total"
  ,"DAC EU Members, Total"
  ,"DAC EU Members + EC, Total"
  ,"Other Multilateral, Total"
  ,"Regional Development Banks, Total"
  #Duplicates
  ,"International Development Association [IDA]"
  ,"World Bank, Total"
  ,"AsDB Special Funds"
  ,"African Development Fund [AfDF]"
  ,"African Development Bank [AfDB]"
  ,"IMF (Concessional Trust Funds)"
  ,"United Nations, Total"
  ,"IDB Special Fund"
  )

crs <- subset(crs,!donor %in% vague_donors)

crs <- crs[order(crs$recipient,-crs$value),]
crs.top10 <- data.table(crs)[,head(.SD,10),by="recipient"]

trans.recip.max <- trans.recip.max[order(trans.recip.max$recipient,-trans.recip.max$iati.value),]
trans.recip.top10 <- trans.recip.max[,head(.SD,10),by="recipient"]

publisher.dict <- c(
  "worldbank"="World Bank Group, Total"    
  ,"asdb"="Asian Development Bank, Total"         
  ,"dfid"="United Kingdom"         
  ,"bmz"="Germany"           
  ,"usaid"="United States"        
  ,"ec-devco"="EU Institutions"     
  ,"ifad"="IFAD"         
  ,"theglobalfund"="Global Fund"
  ,"ausgov"="Australia"       
  ,"minbuza_nl"="Netherlands"   
  ,"unitedstates"="United States" 
  ,"afdb"="African Development Bank, Total"         
  ,"be-dgd"="Belgium"       
  ,"undp"="UNDP"         
  ,"danida"="Denmark"       
  ,"ec-echo"="EU Institutions"      
  ,"gac-amc"="Canada"      
  ,"gavi"="Global Alliance for Vaccines and Immunization [GAVI]"         
  ,"wfp"="WFP"          
  ,"iadb"="Inter-American Development Bank, Total"         
  ,"norad"="Norway"        
  ,"sida"="Sweden"         
  ,"cerf"="CERF"         
  ,"fao"="FAO"          
  ,"unfpa"="UNFPA"        
  ,"ec-near"="EU Institutions"      
  ,"afd"="France"          
  ,"ebrd"="EBRD"         
  ,"idlo"="IDLO"         
  ,"mfat"="New Zealand"
  ,"gavi"="Global Alliance for Vaccines and Immunization [GAVI]"
  ,"jica"="Japan"
  ,"bmgf"="Bill & Melinda Gates Foundation"
  ,"finland_mfa"="Finland"
  ,"theglobalfund"="Global Fund"
  ,"aics"="Italy"
  ,"odakorea"="Korea"
  ,"ofid"="OPEC Fund for International Development [OFID]"
  ,"uasd"="Romania"
  ,"maec"="Spain"
  ,"sdc_ch"="Switzerland"
  ,"unicef"="UNICEF"
)

trans.recip.max$donor = publisher.dict[trans.recip.max$publisher]

setnames(crs,"value","crs.value")
setnames(crs,"year","crs.year")
joint.donors <- merge(crs,trans.recip.max,by=c("recipient","donor"),all=TRUE)
joint.donors$value <- pmax(joint.donors$crs.value,joint.donors$iati.value,na.rm=TRUE)
joint.donors <- joint.donors[order(joint.donors$recipient,-joint.donors$value),]

joint.donors <- joint.donors[order(joint.donors$recipient,-joint.donors$value),]
joint.top10 <- data.table(joint.donors)[,head(.SD,10),by="recipient"]
joint.top10$publishing.to.iati <- as.numeric(!is.na(joint.top10$iati.value))
joint.top10$donor.or.publisher <- joint.top10$donor
joint.top10$donor.or.publisher[which(is.na(joint.top10$donor.or.publisher))] <- joint.top10$publisher[which(is.na(joint.top10$donor.or.publisher))]

write.csv(transactions.aggregate.2017,"transactions_2017.csv",na="",row.names=FALSE)
write.csv(trans.2017.tab,"transactions_2017_by_publisher.csv",na="",row.names=FALSE)
write.csv(budgets.aggregate.17.18.19,"budgets_171819.csv",na="",row.names=FALSE)
write.csv(bud.17.18.19.tab,"budgets_171819_by_publisher.csv",na="",row.names=FALSE)
write.csv(transactions.disaggregate.15.16.17,"transactions_151617_disaggregated.csv",na="",row.names=FALSE)
write.csv(trans.recip.top10,"transactions_by_recipient.csv",na="",row.names=FALSE)
write.csv(crs.top10,"crs_by_recipient.csv",na="",row.names=FALSE)
write.csv(joint.top10,"merged_by_recipient.csv",na="",row.names=FALSE)
