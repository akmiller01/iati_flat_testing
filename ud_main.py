from unfiltered_disagg import *
import pandas as pd
import os
import shutil
from lxml import etree
import platform

if __name__ == '__main__':
    #Initialize flattener class
    iatiflat = IatiFlat()
    
    if platform.system()=="Linux":
        prefix = "/media/alex/Windows/"
    else:
        prefix = "C:/"
    
    #Clean-up of old data; Make sure nothing important is in whatever folder you put here because it will be irrevocably erased
    shutil.rmtree(prefix+"Users/Alex/Documents/Data/IATI/sep/")
    os.mkdir(prefix+"Users/Alex/Documents/Data/IATI/sep/")
    
    
    #Where to look for saved IATI XML via registry-refresher
    rootdir = prefix+'Users/Alex/Documents/Data/IATI-Registry-Refresher/data'
    
    #Predefined header names
    header = iatiflat.header
    full_header = header + ["publisher"]
    header_frame = pd.DataFrame([full_header])
    header_frame.to_csv(prefix+"Users/Alex/Documents/Data/IATI/sep/000header.csv",index=False,header=False,encoding="utf-8")
    
    #Loop through all the folders downloaded via IATI registry refresh, and pass XML roots to our flatten_activities function.
    for subdir, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            publisher = os.path.basename(subdir)
            print filename
            try:
                root = etree.parse(filepath).getroot()
            except etree.XMLSyntaxError:
                continue
            output = iatiflat.flatten_activities(root,publisher)
            if len(output)>0:
                data = pd.DataFrame(output)
                data.columns = header
                data['publisher'] = publisher
                data.to_csv(prefix+"Users/Alex/Documents/Data/IATI/sep/{}.csv".format(filename),index=False,header=False,encoding="utf-8")
                    
    #Once individual (headless) CSVs are written for each donor. It's an easy step to concatenate them into one large document.
    #You may want to consider doing this in code rather than saving each donor's CSVs to disk, but I found this useful for
    #saving progress physically in case the conversion process gets interrupted
    os.system("cat {}Users/Alex/Documents/Data/IATI/sep/*.csv > {}Users/Alex/Documents/Data/IATI/iati_unfiltered_disagg.csv".format(prefix,prefix))