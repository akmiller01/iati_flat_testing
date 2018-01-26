from iatiflat2 import *
import pandas as pd
import os
import shutil
from lxml import etree

if __name__ == '__main__':
    #Initialize flattener class
    iatiflat = IatiFlat()
    
    #Clean-up of old data; Make sure nothing important is in whatever folder you put here because it will be irrevocably erased
    shutil.rmtree("C:/Users/Alex/Documents/Data/IATI/sep/")
    os.mkdir("C:/Users/Alex/Documents/Data/IATI/sep/")
    
    
    #Where to look for saved IATI XML via registry-refresher
    rootdir = 'C:/Users/Alex/Documents/Data/IATI-Registry-Refresher/data'
    
    #Predefined header names
    header = iatiflat.header
    #Dictionary that translates between iati donor code and CRS donor code
    donor_code_lookup = iatiflat.dictionaries["donor_code_lookup"]
    #And a further dictionary to translate between CRS donor code and our internal entity identifier
    donor_di_code_lookup = iatiflat.dictionaries["donor_di_code_lookup"]
    #Write a CSV that just consists of the full header. This will be cat'ed to the top of our concatinated total CSV after all donor CSVs have been written
    full_header = header + ["donor_code","from_di_id"]
    header_frame = pd.DataFrame([full_header])
    header_frame.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/000header.csv",index=False,header=False,encoding="utf-8")
    
    #Loop through all the folders downloaded via IATI registry refresh, and pass XML roots to our flatten_activities function.
    for subdir, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            publisher = os.path.basename(subdir)
            if publisher in donor_code_lookup.keys():
                print filename
                try:
                    root = etree.parse(filepath).getroot()
                except etree.XMLSyntaxError:
                    continue
                output = iatiflat.flatten_activities(root)
                if len(output)>0:
                    data = pd.DataFrame(output)
                    data.columns = header
                    data['donor_code'] = donor_code_lookup[publisher]
                    data['from_di_id'] = donor_di_code_lookup[donor_code_lookup[publisher]]
                    data.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/{}.csv".format(filename),index=False,header=False,encoding="utf-8")
                    
    #Once individual (headless) CSVs are written for each donor. It's an easy step to concatenate them into one large document.
    #You may want to consider doing this in code rather than saving each donor's CSVs to disk, but I found this useful for
    #saving progress physically in case the conversion process gets interrupted
    os.system("cat C:/Users/Alex/Documents/Data/IATI/sep/*.csv > C:/Users/Alex/Documents/Data/IATI/iati.csv")