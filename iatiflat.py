import iati.default
import progressbar
import pandas as pd
from collections import defaultdict
import pdb
import math
from lxml import etree
import os
from io import StringIO

#Probably need to refactor this for multiple sectors, providers, etc.
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

def flatten_activities(root):
    output = []
    try:
        version = root.attrib["version"]
    except KeyError:
        #Default?
        version = '2.02'
    
    activity_len = len(root.findall("iati-activity"))
        
    bar = progressbar.ProgressBar()
    for i in bar(range(0,activity_len)):
        activity = root.xpath('iati-activity[%s]' % (i + 1) )[0]
        
        try:
            vcd = make_versioned_code_dict(version)
        except ValueError:
            continue
            
        child_tags = [child.tag for child in activity.getchildren()]

        secondary_reporter = default_first(activity.xpath("reporting-org/@secondary-reporter"))
        #Set up defaults
        
        #default_donor_org
        default_donor_code = None
        default_donor_text = None
        default_donor_type = None
        if "participating-org" in child_tags:
            participating_orgs = activity.findall("participating-org")
            for p_org in participating_orgs:
                p_org_role = default_first(p_org.xpath("@role"))
                #Ignoring possibility of multiple funders
                if p_org_role==1 or p_org_role=="Funding":
                    default_donor_code = default_first(p_org.xpath("@ref"))
                    default_donor_text = default_first(p_org.xpath("text()"))
                    default_donor_type = default_first(p_org.xpath("@type"))
                    
        #Add crs-add (channel code, ftc, pba) and descriptions here 
        defaults = {}
        default_tags = ["default-currency","default-finance-type","default-aid-type","default-flow-type","recipient-country","recipient-region","sector"]
        for tag in default_tags:
            if tag in activity.attrib.keys():
                defaults[tag] = activity.attrib[tag]
            elif tag in child_tags:
                defaults[tag] = default_first(activity.xpath("{}/@code".format(tag)))
            else:
                defaults[tag] = None
        
        has_transactions = "transaction" in child_tags
        if "crs-add" in child_tags:
            pdb.set_trace()
        if has_transactions:
            transactions = activity.findall("transaction")
            for transaction in transactions:
                transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                # transaction_type = recode_if_not_none(transaction_type_code,vcd["TransactionType"])
                
                transaction_date = default_first(transaction.xpath("transaction-date/@iso-date"))
                year = transaction_date[:4] if transaction_date else None
                
                currency = default_first(transaction.xpath("value/@currency"))
                currency = replace_default_if_none(currency,defaults["default-currency"])
    
                value = default_first(transaction.xpath("value/text()"))
                value_date = default_first(transaction.xpath("value/@value-date"))
                
                transaction_donor_code = default_first(transaction.xpath("provider-org/@ref"))
                transaction_donor_text = default_first(transaction.xpath("provider-org/text()"))
                
                #Introduce some sort of check here, to see if we've replaced one then we've replaced them all
                donor_code = replace_default_if_none(transaction_donor_code,default_donor_code)
                donor_text = replace_default_if_none(transaction_donor_text,default_donor_text)

                provider_activity_id = default_first(transaction.xpath("provider-org/@provider-activity-id"))
                
                sector_code = default_first(transaction.xpath("sector/@code"))
                sector_code = replace_default_if_none(sector_code,defaults["sector"])
                
                # sector = recode_if_not_none(sector_code,vcd["Sector"])
                
                recipient_country_code = default_first(transaction.xpath("recipient-country/@code"))
                recipient_country_code = replace_default_if_none(recipient_country_code,defaults["recipient-country"])
    
                # recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                recipient_region_code = default_first(transaction.xpath("recipient-region/@code"))
                recipient_region_code = replace_default_if_none(recipient_region_code,defaults["recipient-region"])
    
                # recipient_region = recode_if_not_none(recipient_region_code,vcd["Region"])
                
                flow_type_code = default_first(transaction.xpath("flow-type/@code"))
                flow_type_code = replace_default_if_none(flow_type_code,defaults["default-flow-type"])
                    
                disbursement_channel_code = default_first(transaction.xpath("disbursement-channel/@code"))
                
                finance_type_code = default_first(transaction.xpath("finance-type/@code"))
                finance_type_code = replace_default_if_none(finance_type_code,defaults["default-finance-type"])
                
                aid_type_code = default_first(transaction.xpath("aid-type/@code"))
                aid_type_code = replace_default_if_none(aid_type_code,defaults["default-aid-type"])
                # aid_type = recode_if_not_none(aid_type_code,vcd["AidType"])
                
                category = None
                budget_type = None
                b_or_t = "Transaction"
                
                row = [version,secondary_reporter,year,transaction_date,donor_code,donor_text,recipient_country_code,recipient_region_code,flow_type_code,category,finance_type_code,currency,value,aid_type_code,sector_code,disbursement_channel_code,b_or_t,budget_type]
                output.append(row)
            
            has_budget = "budget" in child_tags
            if has_budget:
                budgets = activity.findall("budget")
                for budget in budgets:
                    if "type" in budget.attrib.keys():
                        budget_type = budget.attrib["type"]
                    else:
                        budget_type = None
                        
                    transaction_date = default_first(budget.xpath("period-start/@iso-date"))
                    year = transaction_date[:4] if transaction_date else None
                        
                    value = default_first(budget.xpath("value/text()"))
                    value_date = default_first(budget.xpath("value/@value-date"))
                    currency = default_first(budget.xpath("value/@currency"))
                    currency = replace_default_if_none(currency,defaults["default-currency"])
                    
                    donor_code = default_donor_code
                    donor_text = default_donor_text
                    
                    sector_code = defaults["sector"]
                    # sector = recode_if_not_none(sector_code,vcd["Sector"])
                    
                    recipient_country_code = defaults["recipient-country"]
                    # recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                    recipient_region_code = defaults["recipient-region"]
                    # recipient_region = recode_if_not_none(recipient_region_code,vcd["Region"])
                    
                    flow_type_code = defaults["default-flow-type"]
                    
                    finance_type_code = defaults["default-finance-type"]
                    
                    aid_type_code = defaults["default-aid-type"]
                    
                    category = None
                    disbursement_channel_code = None
                    b_or_t = "Budget"
            
                    row = [version,secondary_reporter,year,transaction_date,donor_code,donor_text,recipient_country_code,recipient_region_code,flow_type_code,category,finance_type_code,currency,value,aid_type_code,sector_code,disbursement_channel_code,b_or_t,budget_type]
                    output.append(row)
    return output
    
if __name__ == '__main__':
    rootdir = 'C:/Users/Alex/Documents/Data/IATI-Registry-Refresher/data'
    for subdir, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            publisher = os.path.basename(subdir)
            print filename
            try:
                root = etree.parse(filepath).getroot()
            except etree.XMLSyntaxError:
                continue
            output = flatten_activities(root)
            if len(output)>0:
                data = pd.DataFrame(output)
                data.columns = ["version","secondary_reporter","year","transaction_date","donor_code","donor_text","recipient_country_code","recipient_region_code","flow_type_code","category","finance_type_code","currency","value","aid_type_code","sector_code","disbursement_channel_code","b_or_t","budget_type"]
                data['publisher'] = publisher
                data.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/{}.csv".format(filename),index=False,header=False,encoding="utf-8")