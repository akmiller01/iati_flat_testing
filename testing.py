import iati.default
import requests
import progressbar
import pandas as pd
import pdb

def makeVersionedCodeDict(version):
    master_dict = {}
    desired_lists = ["TransactionType","Currency","SectorCategory","Country","Region"]
    for desired_list in desired_lists:
        codelist = iati.default.codelist(desired_list,version)
        master_dict[desired_list] = {code.value:code.name for code in codelist.codes}
    return master_dict

activities_raw = requests.get("http://datastore.iatistandard.org/api/1/access/activity.xml?limit=1000").content
activities = iati.Dataset(activities_raw)

ns =  activities.xml_tree.getroot().nsmap
iati_extra = ns['iati-extra']

iati_activities = activities.xml_tree.xpath('iati-activities')[0]
activity_len = len(iati_activities.findall("iati-activity"))

output = []

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
    has_transactions = "transaction" in child_tags
    if has_transactions:
        transactions = activity.findall("transaction")
        for transaction in transactions:
            transaction_type_code = transaction.xpath("transaction-type/@code")[0] if transaction.xpath("transaction-type/@code") else None
            transaction_type = vcd["TransactionType"][transaction_type_code] if transaction_type_code else None
            
            transaction_date = transaction.xpath("transaction-date/@iso-date")[0] if transaction.xpath("transaction-date/@iso-date") else None
            currency = transaction.xpath("value/@currency")[0] if transaction.xpath("value/@currency") else None
            value = transaction.xpath("value/text()")[0] if transaction.xpath("value/text()") else None
            value_date = transaction.xpath("value/@value-date")[0] if transaction.xpath("value/@value-date") else None
            provider_activity_id = transaction.xpath("provider-org/@provider-activity-id")[0] if transaction.xpath("provider-org/@provider-activity-id") else None
            sector_code = transaction.xpath("sector/@code")[0] if transaction.xpath("sector/@code") else None
            sector = vcd["SectorCategory"][sector_code] if sector_code else None
            
            recipient_country_code = transaction.xpath("recipient-country/@code")[0] if transaction.xpath("recipient-country/@code") else None
            recipient_country = vcd["Country"][recipient_country_code] if recipient_country_code else None
            
            recipient_region_code = transaction.xpath("recipient-region/@code")[0] if transaction.xpath("recipient-region/@code") else None
            recipient_region = vcd["Region"][recipient_region_code] if recipient_region_code else None
            
            row = [transaction_type,transaction_date,currency,value,value_date,provider_activity_id,sector,recipient_country,recipient_region]
            output.append(row)
            
data = pd.DataFrame(output)
data.columns = ["transaction_type","transaction_date","currency","value","value_date","provider_activity_id","sector","recipient_country","recipient_region"]
data.to_csv("test_output.csv",index=False)