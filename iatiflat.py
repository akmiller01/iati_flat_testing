import iati.default
import progressbar
import pandas as pd
import pdb
from lxml import etree
import os
from io import StringIO

#Probably need to refactor this for multiple sectors, providers, etc.
def default_first(array):
    #If an array isn't empty, give us the first element
    return array[0] if array is not None and len(array)>0 else None

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
        iati_identifier = default_first(activity.xpath("iati-identifier/text()"))
        
        # Can fail on "1.0"
        # vcd = make_versioned_code_dict(version)
            
        child_tags = [child.tag for child in activity.getchildren()]

        secondary_reporter = default_first(activity.xpath("reporting-org/@secondary-reporter"))
        secondary_reporter = replace_default_if_none(secondary_reporter,"0")
        #Set up defaults
                    
        channel_code = None
        ftc = False
        pba = False
        if "crs-add" in child_tags:
            crs_add = activity.xpath("crs-add")[0]
            crs_add_child_tags = [child.tag for child in crs_add.getchildren()]
            if "channel-code" in crs_add_child_tags:
                channel_code = default_first(crs_add.xpath("channel-code/text()"))
            other_flags = crs_add.findall("other-flags")
            for other_flag in other_flags:
                other_flag_code = default_first(other_flag.xpath("@code"))
                if other_flag_code=="1":
                    ftc = True
                if other_flag_code=="2":
                    pba = True
                    
        if version[:1]=="1":
            long_description = default_first(activity.xpath("description/text()"))
        elif version[:1]=="2":
            long_description = default_first(activity.xpath("description/narrative/text()"))
        else:
            long_description = None
            
        if version[:1]=="1":
            short_description = default_first(activity.xpath("title/text()"))
        elif version[:1]=="2":
            short_description = default_first(activity.xpath("title/narrative/text()"))
        else:
            short_description = None
        
        defaults = {}
        default_tags = ["default-currency","default-finance-type","default-aid-type","default-flow-type"]
        for tag in default_tags:
            if tag in activity.attrib.keys():
                defaults[tag] = activity.attrib[tag]
            elif tag in child_tags:
                defaults[tag] = default_first(activity.xpath("{}/@code".format(tag)))
            else:
                defaults[tag] = None
                
        activity_sector_percentage = 0.0
        activity_recipient_percentage = 0.0
        
        sectors = activity.findall("sector")
        activity_sectors = {}
        for sector in sectors:
            attribs = sector.attrib
            attrib_keys = attribs.keys()
            percentage = attribs['percentage'] if 'percentage' in attrib_keys else None
            activity_sector_percentage += float(percentage) if percentage is not None else 0.0
            code = attribs['code'] if 'code' in attrib_keys else None
            vocabulary = attribs['vocabulary'] if 'vocabulary' in attrib_keys else None
            if vocabulary is None or vocabulary in ["","1","2","DAC","DAC-3"]:
                if code is not None:
                    activity_sectors[code] = float(percentage) if percentage is not None else None
            
        recipient_countries = activity.findall("recipient-country")
        activity_recipients = {}
        for recipient_country in recipient_countries:
            attribs = recipient_country.attrib
            attrib_keys = attribs.keys()
            percentage = attribs['percentage'] if 'percentage' in attrib_keys else None
            activity_recipient_percentage += float(percentage) if percentage is not None else 0.0
            code = attribs['code'] if 'code' in attrib_keys else None
            if code is not None:
                activity_recipients[code] = float(percentage) if percentage is not None else None
            
        recipient_regions = activity.findall("recipient-region")
        for recipient_region in recipient_regions:
            attribs = recipient_region.attrib
            attrib_keys = attribs.keys()
            percentage = attribs['percentage'] if 'percentage' in attrib_keys else None
            activity_recipient_percentage += float(percentage) if percentage is not None else 0.0
            code = attribs['code'] if 'code' in attrib_keys else None
            if code is not None:
                activity_recipients[code] = float(percentage) if percentage is not None else None
            
        #Temporary until we sort out sectors/recipients
        defaults['recipient'] = activity_recipients.keys()[0] if len(activity_recipients.keys())>0 else None
        defaults['sector'] = activity_sectors.keys()[0] if len(activity_sectors.keys())>0 else None
        
        has_transactions = "transaction" in child_tags
        if has_transactions:
            transactions = activity.findall("transaction")
            #Once through the transactions to find the sector sum, sector percents, recipient sum, recipient percents
            transaction_value_sum = 0.0
            transaction_sectors = {}
            transaction_recipients = {}
            for transaction in transactions:
                sector_code = default_first(transaction.xpath("sector/@code"))
                
                recipient_country_code = default_first(transaction.xpath("recipient-country/@code"))
                recipient_region_code = default_first(transaction.xpath("recipient-region/@code"))
                
                recipient_code = replace_default_if_none(recipient_country_code,recipient_region_code)
                
                value = default_first(transaction.xpath("value/text()"))
                try:
                    value = float(value.replace(" ", "")) if value is not None else None
                except ValueError:
                    value = None
                
                if value is not None:
                    if sector_code is not None:
                        transaction_sectors[sector_code] = value
                    if recipient_code is not None:
                        transaction_recipients[recipient_code] = value
                    transaction_value_sum += value
            
            #Once we have the sum, we can calculate percents
            if transaction_value_sum>0:
                for sector_code in transaction_sectors:
                    transaction_sectors[sector_code] = transaction_sectors[sector_code]/transaction_value_sum
                    
                for recipient_code in transaction_recipients:
                    transaction_recipients[recipient_code] = transaction_recipients[recipient_code]/transaction_value_sum
                    
            #Another time through
            for transaction in transactions:
                transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                # transaction_type = recode_if_not_none(transaction_type_code,vcd["TransactionType"])
                
                transaction_date = default_first(transaction.xpath("transaction-date/@iso-date"))
                year = transaction_date[:4] if transaction_date is not None else None
                
                currency = default_first(transaction.xpath("value/@currency"))
                currency = replace_default_if_none(currency,defaults["default-currency"])
    
                value = default_first(transaction.xpath("value/text()"))
                value_date = default_first(transaction.xpath("value/@value-date"))
                
                sector_code = default_first(transaction.xpath("sector/@code"))
                sector_code = replace_default_if_none(sector_code,defaults["sector"])
                
                # sector_vocabulary = default_first(transaction.xpath("sector/@vocabulary"))
                
                # sector = recode_if_not_none(sector_code,vcd["Sector"])
                
                recipient_code = default_first(transaction.xpath("recipient-country/@code"))
                recipient_code = replace_default_if_none(recipient_code,defaults["recipient"])
    
                # recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                # recipient_region_code = default_first(transaction.xpath("recipient-region/@code"))
    
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
                
                row = [len(activity_sectors.keys()),activity_sector_percentage,len(activity_recipients.keys()),activity_recipient_percentage,len(transaction_sectors.keys()),len(transaction_recipients.keys()),version,iati_identifier,secondary_reporter,transaction_type_code,year,transaction_date,recipient_code,flow_type_code,category,finance_type_code,aid_type_code,currency,value,short_description,sector_code,channel_code,long_description,ftc,pba,b_or_t,budget_type]
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
                    year = transaction_date[:4] if transaction_date is not None else None
                        
                    value = default_first(budget.xpath("value/text()"))
                    value_date = default_first(budget.xpath("value/@value-date"))
                    currency = default_first(budget.xpath("value/@currency"))
                    currency = replace_default_if_none(currency,defaults["default-currency"])
                    
                    sector_code = defaults["sector"]
                    # sector = recode_if_not_none(sector_code,vcd["Sector"])
                                        
                    recipient_code = defaults["recipient"]
                    # recipient_country = recode_if_not_none(recipient_country_code,vcd["Country"])
                
                    
                    flow_type_code = defaults["default-flow-type"]
                    
                    finance_type_code = defaults["default-finance-type"]
                    
                    aid_type_code = defaults["default-aid-type"]
                    
                    category = None
                    disbursement_channel_code = None
                    b_or_t = "Budget"
            
                    row = [len(activity_sectors.keys()),activity_sector_percentage,len(activity_recipients.keys()),activity_recipient_percentage,len(transaction_sectors.keys()),len(transaction_recipients.keys()),version,iati_identifier,secondary_reporter,transaction_type_code,year,transaction_date,recipient_code,flow_type_code,category,finance_type_code,aid_type_code,currency,value,short_description,sector_code,channel_code,long_description,ftc,pba,b_or_t,budget_type]
                    output.append(row)
    return output
    
if __name__ == '__main__':
    rootdir = 'C:/Users/Alex/Documents/Data/IATI-Registry-Refresher/data'
    header = ["len_activity_sectors","activity_sector_percentage","len_activity_recipients","activity_recipient_percentage","len_transaction_sectors","len_transaction_recipients","version","iati_identifier","secondary_reporter","transaction_type_code","year","transaction_date","recipient_code","flow_type_code","category","finance_type_code","aid_type_code","currency","value","short_description","sector_code","channel_code","long_description","ftc","pba","b_or_t","budget_type"]
    
    donor_code_lookup = {
        "af":"adaptation-fund"
        ,"afd":"FR"
        ,"afdb":"afdb"
        ,"aics":"IT"
        ,"asdb":"asdb"
        ,"ausgov":"AU"
        ,"be-dgd":"BE"
        ,"bmgf":"bmgf"
        ,"bmz":"DE"
        ,"btc-ctb":"BE"
        ,"cdc":"GB"
        ,"cif":"cif"
        ,"danida":"DK"
        ,"deccadmin":"GB"
        ,"defra_transparency":"GB"
        ,"dfid":"GB"
        ,"doh":"GB"
        ,"dwp":"GB"
        ,"ebrd":"ebrd"
        ,"ec-devco":"EU"
        ,"ec-echo":"EU"
        ,"ec-fpi":"EU"
        ,"ec-near":"EU"
        ,"eib":"EU"
        ,"fao":"fao"
        ,"fco":"GB"
        ,"finance_canada":"CA"
        ,"finland_mfa":"FI"
        ,"gac-amc":"CA"
        ,"gain":"gavi"
        ,"gavi":"gavi"
        ,"hooda":"GB"
        ,"iadb":"idb"
        ,"idrccrdi":"CA"
        ,"ifad":"ifad"
        ,"ifcwbg":"ifc"
        ,"ilo":"international-labour-organisation"
        ,"irishaid":"IE"
        ,"jica":"JP"
        ,"lithuania_mfa":"LT"
        ,"maec":"ES"
        ,"mfat":"NZ"
        ,"minbuza_nl":"NL"
        ,"mrc":"GB"
        ,"norad":"NO"
        ,"odakorea":"KR"
        ,"ofid":"ofid"
        ,"scottish_government":"GB"
        ,"sdc_ch":"CH"
        ,"sida":"SE"
        ,"slovakaid":"SK"
        ,"theglobalfund":"global-fund"
        ,"uasd":"RO"
        ,"ukmod":"GB"
        ,"unaids":"unaids"
        ,"undp":"undp"
        ,"unfpa":"unfpa"
        ,"unicef":"unicef"
        ,"unitedstates":"US"
        ,"usaid":"US"
        ,"wfa":"GB"
        ,"wfp":"wfp"
        ,"who":"who"
        ,"worldbank":"ida"
    }
    #Remove this part if you don't want a header file
    full_header = ["len_activity_sectors","activity_sector_percentage","len_activity_recipients","activity_recipient_percentage","len_transaction_sectors","len_transaction_recipients","version","iati_identifier","secondary_reporter","transaction_type_code","year","transaction_date","recipient_code","flow_type_code","category","finance_type_code","aid_type_code","currency","value","short_description","sector_code","channel_code","long_description","ftc","pba","b_or_t","budget_type","publisher","donor_code"]
    header_frame = pd.DataFrame([full_header])
    header_frame.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/000header.csv",index=False,header=False,encoding="utf-8")
    
    for subdir, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            publisher = os.path.basename(subdir)
            if publisher in donor_code_lookup.keys():
            # if publisher in sorted(donor_code_lookup.keys())[25:]:
                print filename
                try:
                    root = etree.parse(filepath).getroot()
                except etree.XMLSyntaxError:
                    continue
                output = flatten_activities(root)
                if len(output)>0:
                    data = pd.DataFrame(output)
                    data.columns = header
                    data['publisher'] = publisher
                    data['donor_code'] = donor_code_lookup[publisher]
                    data.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/{}.csv".format(filename),index=False,header=False,encoding="utf-8")
                    
    os.system("cat C:/Users/Alex/Documents/Data/IATI/sep/*.csv > C:/Users/Alex/Documents/Data/IATI/iati.csv")