import iati.default
import requests
import progressbar
import pandas as pd
from collections import defaultdict
import pdb

def default_first(array):
    #If an array isn't empty, give us the first element
    return array[0] if array else None

def replace_default_if_none(value,default):
    if value is None:
        return default
    elif str.strip(value) == "":
        return default
    else:
        return value
    
def recode_if_not_none(code,dictionary):
    if code is None:
        return None
    elif str.strip(code) == "":
        return None
    else:
        try:
            return dictionary[code]
        except KeyError:
            return code

def make_versioned_code_dict(version):
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

def flatten_datastore_url(url):
    output = []
    conn = requests.get(url)
    if conn.status_code!=200:
        return 500
    activities_raw = conn.content
    activities = iati.Dataset(activities_raw)
    
    ns =  activities.xml_tree.getroot().nsmap
    iati_extra = ns['iati-extra']
    
    iati_activities = activities.xml_tree.xpath('iati-activities')[0]
    activity_len = len(iati_activities.findall("iati-activity"))
        
    bar = progressbar.ProgressBar()
    for i in bar(range(0,activity_len)):
        activity = activities.xml_tree.xpath('iati-activities/iati-activity[%s]' % (i + 1) )[0]
        version = activity.attrib["{%s}version" % iati_extra]
        
        try:
            vcd = make_versioned_code_dict(version)
        except ValueError:
            continue
            
        child_tags = [child.tag for child in activity.getchildren()]
        #Set up defaults?
        defaults = {}
        default_tags = ["default-currency","default-flow-type","recipient-country","recipient-region","sector"]
        for tag in default_tags:
            if tag in activity.attrib.keys():
                defaults[tag] = activity.attrib[tag]
            elif tag in child_tags:
                defaults[tag] = default_first(activity.xpath("{}/@code".format(tag)))
            else:
                defaults[tag] = None
        has_transactions = "transaction" in child_tags
        if has_transactions:
            transactions = activity.findall("transaction")
            for transaction in transactions:
                transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                transaction_type = vcd["TransactionType"][transaction_type_code] if transaction_type_code else None
                
                transaction_date = default_first(transaction.xpath("transaction-date/@iso-date"))
                
                currency = default_first(transaction.xpath("value/@currency"))
                currency = replace_default_if_none(currency,defaults["default-currency"])
    
                value = default_first(transaction.xpath("value/text()"))
                value_date = default_first(transaction.xpath("value/@value-date"))
                
                provider_activity_id = default_first(transaction.xpath("provider-org/@provider-activity-id"))
                
                sector_code = default_first(transaction.xpath("sector/@code"))
                sector_code = replace_default_if_none(sector_code,defaults["sector"])
                
                sector = recode_if_not_none(sector_code,vcd["Sector"])
                
                recipient_country_code = default_first(transaction.xpath("recipient-country/@code"))
                recipient_country_code = replace_default_if_none(recipient_country_code,defaults["recipient-country"])
    
                recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                recipient_region_code = default_first(transaction.xpath("recipient-region/@code"))
                recipient_region_code = replace_default_if_none(recipient_region_code,defaults["recipient-region"])
    
                recipient_region = recode_if_not_none(recipient_region_code,vcd["Region"])
                
                flow_type_code = default_first(transaction.xpath("flow-type/@code"))
                flow_type_code = replace_default_if_none(flow_type_code,defaults["default-flow-type"])
                    
                disbursement_channel_code = default_first(transaction.xpath("disbursement-channel/@code"))
                
                finance_type_code = default_first(transaction.xpath("finance-type/@code"))
                
                aid_type_code = default_first(transaction.xpath("aid-type/@code"))
                aid_type = recode_if_not_none(aid_type_code,vcd["AidType"])
                
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
                    value = default_first(budget.xpath("value/text()"))
                    value_date = default_first(budget.xpath("value/@value-date"))
                    currency = default_first(budget.xpath("value/@currency"))
                    currency = replace_default_if_none(currency,defaults["default-currency"])
                    
                    sector_code = defaults["sector"]
                    sector = recode_if_not_none(sector_code,vcd["Sector"])
                    
                    recipient_country_code = defaults["recipient-country"]
                    recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                    recipient_region_code = defaults["recipient-region"]
                    recipient_region = recode_if_not_none(recipient_region_code,vcd["Region"])
            
                    row = [version,None,None,currency,value,value_date,None,sector,recipient_country,recipient_region,None,None,None,None,"Budget",budget_type]
                    output.append(row)
    return output
    
if __name__ == '__main__':
    output = []
    i = 0
    while output != 500:
        output = flatten_datastore_url("http://datastore.iatistandard.org/api/1/access/activity.xml?limit=1000&offset={}".format(i))
        if output != 500:
            data = pd.DataFrame(output)
            data.columns = ["iati_version","transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type"]
            data.to_csv("test_output{}.csv".format(i),index=False,encoding="utf-8")
            i += 1000
        print(i)
    #Reduce limit until we get a valid response
    j = 1000
    while output == 500 and j > 0:
        output = flatten_datastore_url("http://datastore.iatistandard.org/api/1/access/activity.xml?limit={}&offset={}".format(j,i))
        j -= 1
        print("Server error, reducing the limit to %s" % j)
    if j > 0:
        data = pd.DataFrame(output)
        data.columns = ["iati_version","transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region","flow_type_code","disbursement_channel","finance_type","aid_type_code","budget_or_transaction","budget_type"]
        data.to_csv("test_output{}.csv".format(i),index=False,encoding="utf-8")