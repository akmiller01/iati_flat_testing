import iati.default
import requests
import progressbar
import pandas as pd
from collections import defaultdict
import pdb

def makeVersionedCodeDict(version):
    if version in ["1.01","1.02","1.03"]:
        version = "1.04"
    master_dict = {}
    desired_lists = ["TransactionType","Currency","Sector","Country","Region","DisbursementChannel","FinanceType","AidType"]
    for desired_list in desired_lists:
        codelist = iati.default.codelist(desired_list,version)
        master_dict[desired_list] = {code.value:code.name for code in codelist.codes}
    if version in ['1.04','1.05']:
        master_dict["TransactionType"] = {
            "QP":"Purchase of Equity"
            ,"C":"Commitment"
            ,"E":"Expenditure"
            ,"D":"Disbursement"
            ,"IR":"Interest Repayment"
            ,"CG":"Credit Guarantee"
            ,"QS":"Sale of Equity"
            ,"R":"Reimbursement"
            ,"LR":"Loan Repayment"
            ,"IF":"Incoming Funds"
        }
    return master_dict

activities_raw = requests.get("http://datastore.iatistandard.org/api/1/access/activity.xml?limit=1000").content
activities = iati.Dataset(activities_raw)

ns =  activities.xml_tree.getroot().nsmap
iati_extra = ns['iati-extra']

iati_activities = activities.xml_tree.xpath('iati-activities')[0]
activity_len = len(iati_activities.findall("iati-activity"))

output = []
# attribs = defaultdict()

bar = progressbar.ProgressBar()
for i in bar(range(0,activity_len)):
    activity = activities.xml_tree.xpath('iati-activities/iati-activity[%s]' % (i + 1) )[0]
    version = activity.attrib["{%s}version" % iati_extra]
    
    try:
        vcd = makeVersionedCodeDict(version)
    except ValueError:
        #Fails on 1.01, 1.02, 1.03
        #Also 1.04 and 1.05 return blank names
        continue
        
    child_tags = [child.tag for child in activity.getchildren()]
    #Set up defaults?
    if "default-currency" in activity.attrib.keys():
        default_currency = activity.attrib["default-currency"]
    else:
        default_currency = None
    if "default-flow-type" in child_tags:
        default_flow_type_code = activity.xpath("default_flow_type/@code")[0] if activity.xpath("default_flow_type/@code") else None
    else:
        default_flow_type_code = None
    if "recipient-country" in child_tags:
        default_recipient_county_code = activity.xpath("recipient-country/@code")[0] if activity.xpath("recipient-country/@code") else None
    else:
        default_recipient_country_code = None
    if "recipient_region" in child_tags:
        default_recipient_region_code = activity.xpath("recipient-region/@code")[0] if activity.xpath("recipient-region/@code") else None
    else:
        default_recipient_region_code = None
    if "sector" in child_tags:
        default_sector_code = activity.xpath("sector/@code")[0] if activity.xpath("sector/@code") else None
    else:
        default_sector_code = None
    if "location" in child_tags:
        pass #We could geocode this if we're feeling insane
    has_transactions = "transaction" in child_tags
    if has_transactions:
        transactions = activity.findall("transaction")
        for transaction in transactions:
            #As described in Google spreadsheet
            transaction_type_code = transaction.xpath("transaction-type/@code")[0] if transaction.xpath("transaction-type/@code") else None
            transaction_type = vcd["TransactionType"][transaction_type_code] if transaction_type_code else None
            
            transaction_date = transaction.xpath("transaction-date/@iso-date")[0] if transaction.xpath("transaction-date/@iso-date") else None
            currency = transaction.xpath("value/@currency")[0] if transaction.xpath("value/@currency") else None
            if currency is None:
                currency = default_currency
            value = transaction.xpath("value/text()")[0] if transaction.xpath("value/text()") else None
            value_date = transaction.xpath("value/@value-date")[0] if transaction.xpath("value/@value-date") else None
            provider_activity_id = transaction.xpath("provider-org/@provider-activity-id")[0] if transaction.xpath("provider-org/@provider-activity-id") else None
            sector_code = transaction.xpath("sector/@code")[0] if transaction.xpath("sector/@code") else None
            if sector_code is None:
                sector_code = default_sector_code
            sector = vcd["Sector"][sector_code] if sector_code else None
            
            recipient_country_code = transaction.xpath("recipient-country/@code")[0] if transaction.xpath("recipient-country/@code") else None
            if recipient_country_code is None:
                recipient_country_code = default_recipient_country_code
            recipient_country = vcd["Country"][recipient_country_code] if recipient_country_code else None
            
            recipient_region_code = transaction.xpath("recipient-region/@code")[0] if transaction.xpath("recipient-region/@code") else None
            if recipient_region_code is None:
                recipient_region_code = default_recipient_region_code
            recipient_region = vcd["Region"][recipient_region_code] if recipient_region_code else None
            
            #Additional from 15 ODA rows as described in email
            flow_type_code = transaction.xpath("flow-type/@code")[0] if transaction.xpath("flow-type/@code") else None
            if flow_type_code is None:
                flow_type_code = default_flow_type_code
                
            disbursement_channel_code = transaction.xpath("disbursement-channel/@code")[0] if transaction.xpath("disbursement-channel/@code") else None
            # try:
            #     disbursement_channel = vcd["DisbursementChannel"][disbursement_channel_code] if disbursement_channel_code else None
            # except KeyError:
            #     disbursement_channel = disbursement_channel_code
            #Most don't correspond to codelist
            
            finance_type_code = transaction.xpath("finance-type/@code")[0] if transaction.xpath("finance-type/@code") else None
            # finance_type = vcd["DisbursementChannel"][finance_type_code] if finance_type_code else None
            #Most don't correspond to codelist
            
            aid_type_code = transaction.xpath("aid-type/@code")[0] if transaction.xpath("aid-type/@code") else None
            aid_type = vcd["AidType"][aid_type_code] if aid_type_code else None
            
            row = [version,transaction_type,transaction_date,currency,value,value_date,provider_activity_id,sector,recipient_country,recipient_region,flow_type_code,disbursement_channel_code,finance_type_code,aid_type,"Transaction",None]
            output.append(row)
        
        has_budget = "budget" in child_tags
        if has_budget:
            budgets = activity.findall("budget")
            for budget in budgets:
                if "type" in budget.attrib.keys():
                    budget_type = budget.attrib["type"]
                else:
                    budget_type = None
                value = budget.xpath("value/text()")[0] if budget.xpath("value/text()") else None
                value_date = budget.xpath("value/@value-date")[0] if budget.xpath("value/@value-date") else None
                currency = budget.xpath("value/@currency")[0] if budget.xpath("value/@currency") else None
                if currency is None:
                    currency = default_currency
                
                sector_code = default_sector_code
                sector = vcd["Sector"][sector_code] if sector_code else None
                
                recipient_country_code = default_recipient_country_code
                recipient_country = vcd["Country"][recipient_country_code] if recipient_country_code else None
            
                recipient_region_code = default_recipient_region_code
                recipient_region = vcd["Region"][recipient_region_code] if recipient_region_code else None
        
                row = [version,None,None,currency,value,value_date,None,sector,recipient_country,recipient_region,None,None,None,None,"Budget",budget_type]
                output.append(row)
            
# print(attribs.keys())
data = pd.DataFrame(output)
data.columns = ["iati_version","transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type"]
data.to_csv("test_output.csv",index=False,encoding="utf-8")