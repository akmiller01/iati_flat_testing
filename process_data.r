library(data.table)
library(readr)

setwd("C:/Users/Alex/Documents/Data/IATI/")

agg <- read_csv("iati_unfiltered_agg.csv")
dagg <- read_csv("iati_unfiltered_disagg.csv")

transactions.aggregate <- subset(agg,budget_or_transaction=="Transaction")
budgets.aggregate <- subset(agg,budget_or_transaction=="Budget")

transactions.aggregate.2017 <- subset(transactions.aggregate,year==2017)
trans.2017.tab <- data.table(transactions.aggregate.2017)[,.(value=sum(usd_disbursement,na.rm=TRUE)),by=.(publisher,year)]

budgets.aggregate.16.17.18 <- subset(budgets.aggregate,year %in% c(2016,2017,2018))

bud.16.17.18.tab <- data.table(budgets.aggregate.16.17.18)[,.(value=sum(usd_disbursement,na.rm=TRUE)),by=.(publisher,year)]

write.csv(transactions.aggregate.2017,"transactions_2017.csv",na="",row.names=FALSE)
write.csv(trans.2017.tab,"transactions_2017_by_publisher.csv",na="",row.names=FALSE)
write.csv(budgets.aggregate.16.17.18,"budgets_161718.csv",na="",row.names=FALSE)
write.csv(bud.16.17.18.tab,"budgets_161718_by_publisher.csv",na="",row.names=FALSE)