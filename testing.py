import iati.default
import requests
import pdb

country_codelist = iati.default.codelist('Country',version='2.02')
country_dict = {code.value:code.name for code in country_codelist.codes}

# print("US: {}".format(country_dict['US']))

activities_raw = requests.get("http://datastore.iatistandard.org/api/1/access/activity.xml").content
# transactions_raw = requests.get("http://datastore.iatistandard.org/api/1/access/transaction.xml").content
# budgets_raw = requests.get("http://datastore.iatistandard.org/api/1/access/budget.xml").content

activities = iati.Dataset(activities_raw)
# transactions = iati.Dataset(transactions_raw) ### Doesn't work
# budgets = iati.Dataset(budgets_raw) ### Doesn't work

titles = activities.xml_tree.xpath('iati-activities/iati-activity/title/narrative/text()')

pdb.set_trace()