import iati.default
import progressbar
import pandas as pd
import pdb
from lxml import etree
import os
from io import StringIO
import shutil

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
            return None
        
# def convert_usd(value,year,currency,ratedf):
#     if value==0:
#         return 0
#     elif value is None or year is None or currency is None:
#         return None
#     thisRate = ratedf[(ratedf.currency==currency) & (ratedf.year==year)]
#     if thisRate['rate'].count()>0:
#         conversion_factor = thisRate['rate'].values[0]
#         if conversion_factor>0:
#             return value*conversion_factor
#         else:
#             return None
#     else:
#         return None

def convert_usd(value,year,currency,ratedf):
    if value==0:
        return 0
    elif value is None or year is None or currency is None:
        return None
    try:
        conversion_factor = ratedf[currency][year]
        if conversion_factor>0:
            return value*conversion_factor
        else:
            return None
    except KeyError:
        return None
    
ratedf = {																																												
"AUD":{1980:1.139517172,1981:1.149313491,1982:1.017393998,1983:0.902378871,1984:0.879572797,1985:0.700799351,1986:0.670875651,1987:0.700857565,1988:0.784216442,1989:0.792528112,1990:0.781289797,1991:0.7790979,1992:0.735299284,1993:0.680116413,1994:0.731674124,1995:0.741496187,1996:0.782945437,1997:0.744062837,1998:0.62940068,1999:0.645332247,2000:0.582346532,2001:0.517635943,2002:0.543902648,2003:0.651884045,2004:0.736578578,2005:0.763843802,2006:0.75334984,2007:0.838560795,2008:0.855264574,2009:0.791303713,2010:0.919499092,2011:1.032212708,2012:1.035799755,2013:0.96842634,2014:0.90269528,2015:0.7526124,2016:0.743888756,2017:0.771955602,2018:0.789655036,2019:0.791796204,2020:0.788861628,2021:0.783152088,2022:0.777451106}
,"CAD":{1980:0.855250392,1981:0.834120086,1982:0.810615012,1983:0.811430314,1984:0.772142108,1985:0.732361592,1986:0.719696825,1987:0.754177988,1988:0.81258358,1989:0.844626367,1990:0.857091733,1991:0.872819995,1992:0.827353743,1993:0.775172977,1994:0.732277231,1995:0.728653406,1996:0.733433058,1997:0.7222398,1998:0.674122875,1999:0.673006085,2000:0.673378508,2001:0.645700808,2002:0.637252281,2003:0.713818518,2004:0.768619974,2005:0.825295619,2006:0.881590155,2007:0.931012525,2008:0.937171907,2009:0.874813461,2010:0.9707201,2011:1.010580133,2012:1.000812483,2013:0.971065558,2014:0.904073234,2015:0.781801164,2016:0.754489175,2017:0.769638055,2018:0.790646334,2019:0.792156315,2020:0.791417789,2021:0.789644816,2022:0.788117677}
,"DKK":{1980:0.177465344,1981:0.14041667,1982:0.120033613,1983:0.109358687,1984:0.096572781,1985:0.094407143,1986:0.123628174,1987:0.146217333,1988:0.148574778,1989:0.136827733,1990:0.161599987,1991:0.156380713,1992:0.165718867,1993:0.154243666,1994:0.157236529,1995:0.178528736,1996:0.172463107,1997:0.151429726,1998:0.149246998,1999:0.143341111,2000:0.12373701,2001:0.120172713,2002:0.126676272,2003:0.151827979,2004:0.166912129,2005:0.166766605,2006:0.168163661,2007:0.183698844,2008:0.196150366,2009:0.186536774,2010:0.177806824,2011:0.186264318,2012:0.172637813,2013:0.178052596,2014:0.178174793,2015:0.148634723,2016:0.148550402,2017:0.151266732,2018:0.157920672,2019:0.157969075,2020:0.157569639,2021:0.156965205,2022:0.15641118}
,"EUR":{1980:1.077882204,1981:0.868843086,1982:0.806973023,1983:0.767762198,1984:0.689588619,1985:0.669879209,1986:0.90468713,1987:1.089930533,1988:1.115987461,1989:1.041742364,1990:1.213538639,1991:1.183126978,1992:1.255549395,1993:1.183704212,1994:1.208017309,1995:1.366263798,1996:1.300236202,1997:1.129454168,1998:1.113076805,1999:1.066815021,2000:0.924021489,2001:0.895623552,2002:0.944419248,2003:1.130827718,2004:1.243304031,2005:1.245755065,2006:1.255648595,2007:1.370635795,2008:1.471714538,2009:1.392797568,2010:1.326893948,2011:1.391407707,2012:1.285573514,2013:1.328155783,2014:1.328841557,2015:1.109624957,2016:1.106608355,2017:1.127788302,2018:1.176396602,2019:1.181763704,2020:1.183642918,2021:1.17951761,2022:1.174472193}
,"JPY":{1980:0.004410332,1981:0.004535417,1982:0.004016638,1983:0.004210541,1984:0.004210282,1985:0.004193114,1986:0.005935684,1987:0.006915719,1988:0.007804625,1989:0.007249624,1990:0.006907964,1991:0.007433207,1992:0.007896326,1993:0.008994106,1994:0.009785071,1995:0.01063485,1996:0.009193525,1997:0.008266923,1998:0.007642782,1999:0.008748262,2000:0.009278992,2001:0.008230816,2002:0.007975401,2003:0.00862897,2004:0.009243936,2005:0.009073996,2006:0.00859869,2007:0.008492314,2008:0.00967497,2009:0.010687175,2010:0.011392132,2011:0.012530227,2012:0.012532827,2013:0.010246357,2014:0.009438878,2015:0.008261456,2016:0.009191777,2017:0.00897624,2018:0.009164911,2019:0.009251302,2020:0.009239746,2021:0.009259585,2022:0.009288283}
,"NZD":{1980:0.97417485,1981:0.869947667,1982:0.751846812,1983:0.668801382,1984:0.578488222,1985:0.498406233,1986:0.523911505,1987:0.592206543,1988:0.655959926,1989:0.598457067,1990:0.596948357,1991:0.579146012,1992:0.538125178,1993:0.540737254,1994:0.593691751,1995:0.656438611,1996:0.687631299,1997:0.663025275,1998:0.536657058,1999:0.529547275,2000:0.457370235,2001:0.420640327,2002:0.464225592,2003:0.58226722,2004:0.664008419,2005:0.704355401,2006:0.649502654,2007:0.736125506,2008:0.714574205,2009:0.63414164,2010:0.721296177,2011:0.791166446,2012:0.810575543,2013:0.820528926,2014:0.830839561,2015:0.700273085,2016:0.696963421,2017:0.722302743,2018:0.736665879,2019:0.738869025,2020:0.739069243,2021:0.738438735,2022:0.737623088}
,"NOK":{1980:0.202489011,1981:0.17425359,1982:0.154957027,1983:0.13706225,1984:0.122571996,1985:0.116350731,1986:0.135267643,1987:0.148438435,1988:0.153459502,1989:0.144853133,1990:0.159757821,1991:0.154290603,1992:0.160980355,1993:0.140597546,1994:0.141649475,1995:0.157868561,1996:0.155045816,1997:0.141391927,1998:0.132549055,1999:0.128241877,2000:0.113624637,2001:0.111222465,2002:0.125256621,2003:0.140539746,2004:0.148261401,2005:0.155197665,2006:0.155911673,2007:0.170599878,2008:0.177304926,2009:0.159024702,2010:0.165448819,2011:0.17842472,2012:0.171895135,2013:0.170212697,2014:0.158688257,2015:0.124005512,2016:0.119047726,2017:0.118606067,2018:0.11795433,2019:0.116157731,2020:0.113787546,2021:0.111320305,2022:0.108939779}
,"CHF":{1980:0.596763189,1981:0.509260644,1982:0.492634757,1983:0.476420022,1984:0.425648481,1985:0.407176788,1986:0.556087834,1987:0.670756277,1988:0.683497408,1989:0.611410382,1990:0.719968083,1991:0.697523728,1992:0.711414334,1993:0.676842046,1994:0.731272328,1995:0.845923023,1996:0.809151422,1997:0.689140153,1998:0.689813937,1999:0.665732958,2000:0.592212696,2001:0.592668198,2002:0.641678813,2003:0.742731287,2004:0.804217587,2005:0.803193235,2006:0.797602309,2007:0.833133816,2008:0.925566289,2009:0.921177644,2010:0.95885936,2011:1.126074277,2012:1.066457035,2013:1.07886084,2014:1.091523697,2015:1.039089418,2016:1.01498266,2017:1.020639364,2018:1.038411784,2019:1.043487965,2020:1.045613409,2021:1.04534651,2022:1.044373164}
,"GBP":{1980:2.32628255,1981:2.027903422,1982:1.750519422,1983:1.516993365,1984:1.336335286,1985:1.296331166,1986:1.467005831,1987:1.638903042,1988:1.781361189,1989:1.639704073,1990:1.784712982,1991:1.769367857,1992:1.765524745,1993:1.502019263,1994:1.531605042,1995:1.578466878,1996:1.561740396,1997:1.637694852,1998:1.656412066,1999:1.618224548,2000:1.516105186,2001:1.439964304,2002:1.501258685,2003:1.634373725,2004:1.831799852,2005:1.820401071,2006:1.842629791,2007:2.001679415,2008:1.853244234,2009:1.564477883,2010:1.546113395,2011:1.603604799,2012:1.585306416,2013:1.564467053,2014:1.647422194,2015:1.528959574,2016:1.35550518,2017:1.278857098,2018:1.285666251,2019:1.275525123,2020:1.263879967,2021:1.25191965,2022:1.240450746}
,"USD":{1980:1,1981:1,1982:1,1983:1,1984:1,1985:1,1986:1,1987:1,1988:1,1989:1,1990:1,1991:1,1992:1,1993:1,1994:1,1995:1,1996:1,1997:1,1998:1,1999:1,2000:1,2001:1,2002:1,2003:1,2004:1,2005:1,2006:1,2007:1,2008:1,2009:1,2010:1,2011:1,2012:1,2013:1,2014:1,2015:1,2016:1,2017:1,2018:1,2019:1,2020:1,2021:1,2022:1}
,"XDR":{1980:0,1981:0.849669143,1982:0.90850397,1983:0.936560464,1984:0.977321369,1985:0.986526268,1986:0.85214274,1987:0.773748051,1988:0.745580463,1989:0.780900617,1990:0.737135139,1991:0.732009702,1992:0.710154778,1993:0.716315481,1994:0.698574243,1995:0.65983875,1996:0.68877679,1997:0.726835133,1998:0.736969368,1999:0.731386642,2000:0.758990484,2001:0.783971837,2002:0.773218029,2003:0.713999837,2004:0.675328633,2005:0.677590113,2006:0.679903131,2007:0.653823024,2008:0.635019892,2009:0.649513669,2010:0.655705877,2011:0.633741293,2012:0.653151814,2013:0.658074197,2014:0.658697093,2015:0.714973903,2016:0.719540519,2017:0.722092665,2018:0,2019:0,2020:0,2021:0,2022:0}
}																																										
    
# ratedf = pd.DataFrame(
#     [
#         ["AUD",1980,1.139517172]
#         ,["AUD",1981,1.149313491]
#         ,["AUD",1982,1.017393998]
#         ,["AUD",1983,0.902378871]
#         ,["AUD",1984,0.879572797]
#         ,["AUD",1985,0.700799351]
#         ,["AUD",1986,0.670875651]
#         ,["AUD",1987,0.700857565]
#         ,["AUD",1988,0.784216442]
#         ,["AUD",1989,0.792528112]
#         ,["AUD",1990,0.781289797]
#         ,["AUD",1991,0.7790979]
#         ,["AUD",1992,0.735299284]
#         ,["AUD",1993,0.680116413]
#         ,["AUD",1994,0.731674124]
#         ,["AUD",1995,0.741496187]
#         ,["AUD",1996,0.782945437]
#         ,["AUD",1997,0.744062837]
#         ,["AUD",1998,0.62940068]
#         ,["AUD",1999,0.645332247]
#         ,["AUD",2000,0.582346532]
#         ,["AUD",2001,0.517635943]
#         ,["AUD",2002,0.543902648]
#         ,["AUD",2003,0.651884045]
#         ,["AUD",2004,0.736578578]
#         ,["AUD",2005,0.763843802]
#         ,["AUD",2006,0.75334984]
#         ,["AUD",2007,0.838560795]
#         ,["AUD",2008,0.855264574]
#         ,["AUD",2009,0.791303713]
#         ,["AUD",2010,0.919499092]
#         ,["AUD",2011,1.032212708]
#         ,["AUD",2012,1.035799755]
#         ,["AUD",2013,0.96842634]
#         ,["AUD",2014,0.90269528]
#         ,["AUD",2015,0.7526124]
#         ,["AUD",2016,0.743888756]
#         ,["AUD",2017,0.771955602]
#         ,["AUD",2018,0.789655036]
#         ,["AUD",2019,0.791796204]
#         ,["AUD",2020,0.788861628]
#         ,["AUD",2021,0.783152088]
#         ,["AUD",2022,0.777451106]
#         ,["CAD",1980,0.855250392]
#         ,["CAD",1981,0.834120086]
#         ,["CAD",1982,0.810615012]
#         ,["CAD",1983,0.811430314]
#         ,["CAD",1984,0.772142108]
#         ,["CAD",1985,0.732361592]
#         ,["CAD",1986,0.719696825]
#         ,["CAD",1987,0.754177988]
#         ,["CAD",1988,0.81258358]
#         ,["CAD",1989,0.844626367]
#         ,["CAD",1990,0.857091733]
#         ,["CAD",1991,0.872819995]
#         ,["CAD",1992,0.827353743]
#         ,["CAD",1993,0.775172977]
#         ,["CAD",1994,0.732277231]
#         ,["CAD",1995,0.728653406]
#         ,["CAD",1996,0.733433058]
#         ,["CAD",1997,0.7222398]
#         ,["CAD",1998,0.674122875]
#         ,["CAD",1999,0.673006085]
#         ,["CAD",2000,0.673378508]
#         ,["CAD",2001,0.645700808]
#         ,["CAD",2002,0.637252281]
#         ,["CAD",2003,0.713818518]
#         ,["CAD",2004,0.768619974]
#         ,["CAD",2005,0.825295619]
#         ,["CAD",2006,0.881590155]
#         ,["CAD",2007,0.931012525]
#         ,["CAD",2008,0.937171907]
#         ,["CAD",2009,0.874813461]
#         ,["CAD",2010,0.9707201]
#         ,["CAD",2011,1.010580133]
#         ,["CAD",2012,1.000812483]
#         ,["CAD",2013,0.971065558]
#         ,["CAD",2014,0.904073234]
#         ,["CAD",2015,0.781801164]
#         ,["CAD",2016,0.754489175]
#         ,["CAD",2017,0.769638055]
#         ,["CAD",2018,0.790646334]
#         ,["CAD",2019,0.792156315]
#         ,["CAD",2020,0.791417789]
#         ,["CAD",2021,0.789644816]
#         ,["CAD",2022,0.788117677]
#         ,["DKK",1980,0.177465344]
#         ,["DKK",1981,0.14041667]
#         ,["DKK",1982,0.120033613]
#         ,["DKK",1983,0.109358687]
#         ,["DKK",1984,0.096572781]
#         ,["DKK",1985,0.094407143]
#         ,["DKK",1986,0.123628174]
#         ,["DKK",1987,0.146217333]
#         ,["DKK",1988,0.148574778]
#         ,["DKK",1989,0.136827733]
#         ,["DKK",1990,0.161599987]
#         ,["DKK",1991,0.156380713]
#         ,["DKK",1992,0.165718867]
#         ,["DKK",1993,0.154243666]
#         ,["DKK",1994,0.157236529]
#         ,["DKK",1995,0.178528736]
#         ,["DKK",1996,0.172463107]
#         ,["DKK",1997,0.151429726]
#         ,["DKK",1998,0.149246998]
#         ,["DKK",1999,0.143341111]
#         ,["DKK",2000,0.12373701]
#         ,["DKK",2001,0.120172713]
#         ,["DKK",2002,0.126676272]
#         ,["DKK",2003,0.151827979]
#         ,["DKK",2004,0.166912129]
#         ,["DKK",2005,0.166766605]
#         ,["DKK",2006,0.168163661]
#         ,["DKK",2007,0.183698844]
#         ,["DKK",2008,0.196150366]
#         ,["DKK",2009,0.186536774]
#         ,["DKK",2010,0.177806824]
#         ,["DKK",2011,0.186264318]
#         ,["DKK",2012,0.172637813]
#         ,["DKK",2013,0.178052596]
#         ,["DKK",2014,0.178174793]
#         ,["DKK",2015,0.148634723]
#         ,["DKK",2016,0.148550402]
#         ,["DKK",2017,0.151266732]
#         ,["DKK",2018,0.157920672]
#         ,["DKK",2019,0.157969075]
#         ,["DKK",2020,0.157569639]
#         ,["DKK",2021,0.156965205]
#         ,["DKK",2022,0.15641118]
#         ,["EUR",1980,1.077882204]
#         ,["EUR",1981,0.868843086]
#         ,["EUR",1982,0.806973023]
#         ,["EUR",1983,0.767762198]
#         ,["EUR",1984,0.689588619]
#         ,["EUR",1985,0.669879209]
#         ,["EUR",1986,0.90468713]
#         ,["EUR",1987,1.089930533]
#         ,["EUR",1988,1.115987461]
#         ,["EUR",1989,1.041742364]
#         ,["EUR",1990,1.213538639]
#         ,["EUR",1991,1.183126978]
#         ,["EUR",1992,1.255549395]
#         ,["EUR",1993,1.183704212]
#         ,["EUR",1994,1.208017309]
#         ,["EUR",1995,1.366263798]
#         ,["EUR",1996,1.300236202]
#         ,["EUR",1997,1.129454168]
#         ,["EUR",1998,1.113076805]
#         ,["EUR",1999,1.066815021]
#         ,["EUR",2000,0.924021489]
#         ,["EUR",2001,0.895623552]
#         ,["EUR",2002,0.944419248]
#         ,["EUR",2003,1.130827718]
#         ,["EUR",2004,1.243304031]
#         ,["EUR",2005,1.245755065]
#         ,["EUR",2006,1.255648595]
#         ,["EUR",2007,1.370635795]
#         ,["EUR",2008,1.471714538]
#         ,["EUR",2009,1.392797568]
#         ,["EUR",2010,1.326893948]
#         ,["EUR",2011,1.391407707]
#         ,["EUR",2012,1.285573514]
#         ,["EUR",2013,1.328155783]
#         ,["EUR",2014,1.328841557]
#         ,["EUR",2015,1.109624957]
#         ,["EUR",2016,1.106608355]
#         ,["EUR",2017,1.127788302]
#         ,["EUR",2018,1.176396602]
#         ,["EUR",2019,1.181763704]
#         ,["EUR",2020,1.183642918]
#         ,["EUR",2021,1.17951761]
#         ,["EUR",2022,1.174472193]
#         ,["JPY",1980,0.004410332]
#         ,["JPY",1981,0.004535417]
#         ,["JPY",1982,0.004016638]
#         ,["JPY",1983,0.004210541]
#         ,["JPY",1984,0.004210282]
#         ,["JPY",1985,0.004193114]
#         ,["JPY",1986,0.005935684]
#         ,["JPY",1987,0.006915719]
#         ,["JPY",1988,0.007804625]
#         ,["JPY",1989,0.007249624]
#         ,["JPY",1990,0.006907964]
#         ,["JPY",1991,0.007433207]
#         ,["JPY",1992,0.007896326]
#         ,["JPY",1993,0.008994106]
#         ,["JPY",1994,0.009785071]
#         ,["JPY",1995,0.01063485]
#         ,["JPY",1996,0.009193525]
#         ,["JPY",1997,0.008266923]
#         ,["JPY",1998,0.007642782]
#         ,["JPY",1999,0.008748262]
#         ,["JPY",2000,0.009278992]
#         ,["JPY",2001,0.008230816]
#         ,["JPY",2002,0.007975401]
#         ,["JPY",2003,0.00862897]
#         ,["JPY",2004,0.009243936]
#         ,["JPY",2005,0.009073996]
#         ,["JPY",2006,0.00859869]
#         ,["JPY",2007,0.008492314]
#         ,["JPY",2008,0.00967497]
#         ,["JPY",2009,0.010687175]
#         ,["JPY",2010,0.011392132]
#         ,["JPY",2011,0.012530227]
#         ,["JPY",2012,0.012532827]
#         ,["JPY",2013,0.010246357]
#         ,["JPY",2014,0.009438878]
#         ,["JPY",2015,0.008261456]
#         ,["JPY",2016,0.009191777]
#         ,["JPY",2017,0.00897624]
#         ,["JPY",2018,0.009164911]
#         ,["JPY",2019,0.009251302]
#         ,["JPY",2020,0.009239746]
#         ,["JPY",2021,0.009259585]
#         ,["JPY",2022,0.009288283]
#         ,["NZD",1980,0.97417485]
#         ,["NZD",1981,0.869947667]
#         ,["NZD",1982,0.751846812]
#         ,["NZD",1983,0.668801382]
#         ,["NZD",1984,0.578488222]
#         ,["NZD",1985,0.498406233]
#         ,["NZD",1986,0.523911505]
#         ,["NZD",1987,0.592206543]
#         ,["NZD",1988,0.655959926]
#         ,["NZD",1989,0.598457067]
#         ,["NZD",1990,0.596948357]
#         ,["NZD",1991,0.579146012]
#         ,["NZD",1992,0.538125178]
#         ,["NZD",1993,0.540737254]
#         ,["NZD",1994,0.593691751]
#         ,["NZD",1995,0.656438611]
#         ,["NZD",1996,0.687631299]
#         ,["NZD",1997,0.663025275]
#         ,["NZD",1998,0.536657058]
#         ,["NZD",1999,0.529547275]
#         ,["NZD",2000,0.457370235]
#         ,["NZD",2001,0.420640327]
#         ,["NZD",2002,0.464225592]
#         ,["NZD",2003,0.58226722]
#         ,["NZD",2004,0.664008419]
#         ,["NZD",2005,0.704355401]
#         ,["NZD",2006,0.649502654]
#         ,["NZD",2007,0.736125506]
#         ,["NZD",2008,0.714574205]
#         ,["NZD",2009,0.63414164]
#         ,["NZD",2010,0.721296177]
#         ,["NZD",2011,0.791166446]
#         ,["NZD",2012,0.810575543]
#         ,["NZD",2013,0.820528926]
#         ,["NZD",2014,0.830839561]
#         ,["NZD",2015,0.700273085]
#         ,["NZD",2016,0.696963421]
#         ,["NZD",2017,0.722302743]
#         ,["NZD",2018,0.736665879]
#         ,["NZD",2019,0.738869025]
#         ,["NZD",2020,0.739069243]
#         ,["NZD",2021,0.738438735]
#         ,["NZD",2022,0.737623088]
#         ,["NOK",1980,0.202489011]
#         ,["NOK",1981,0.17425359]
#         ,["NOK",1982,0.154957027]
#         ,["NOK",1983,0.13706225]
#         ,["NOK",1984,0.122571996]
#         ,["NOK",1985,0.116350731]
#         ,["NOK",1986,0.135267643]
#         ,["NOK",1987,0.148438435]
#         ,["NOK",1988,0.153459502]
#         ,["NOK",1989,0.144853133]
#         ,["NOK",1990,0.159757821]
#         ,["NOK",1991,0.154290603]
#         ,["NOK",1992,0.160980355]
#         ,["NOK",1993,0.140597546]
#         ,["NOK",1994,0.141649475]
#         ,["NOK",1995,0.157868561]
#         ,["NOK",1996,0.155045816]
#         ,["NOK",1997,0.141391927]
#         ,["NOK",1998,0.132549055]
#         ,["NOK",1999,0.128241877]
#         ,["NOK",2000,0.113624637]
#         ,["NOK",2001,0.111222465]
#         ,["NOK",2002,0.125256621]
#         ,["NOK",2003,0.140539746]
#         ,["NOK",2004,0.148261401]
#         ,["NOK",2005,0.155197665]
#         ,["NOK",2006,0.155911673]
#         ,["NOK",2007,0.170599878]
#         ,["NOK",2008,0.177304926]
#         ,["NOK",2009,0.159024702]
#         ,["NOK",2010,0.165448819]
#         ,["NOK",2011,0.17842472]
#         ,["NOK",2012,0.171895135]
#         ,["NOK",2013,0.170212697]
#         ,["NOK",2014,0.158688257]
#         ,["NOK",2015,0.124005512]
#         ,["NOK",2016,0.119047726]
#         ,["NOK",2017,0.118606067]
#         ,["NOK",2018,0.11795433]
#         ,["NOK",2019,0.116157731]
#         ,["NOK",2020,0.113787546]
#         ,["NOK",2021,0.111320305]
#         ,["NOK",2022,0.108939779]
#         ,["CHF",1980,0.596763189]
#         ,["CHF",1981,0.509260644]
#         ,["CHF",1982,0.492634757]
#         ,["CHF",1983,0.476420022]
#         ,["CHF",1984,0.425648481]
#         ,["CHF",1985,0.407176788]
#         ,["CHF",1986,0.556087834]
#         ,["CHF",1987,0.670756277]
#         ,["CHF",1988,0.683497408]
#         ,["CHF",1989,0.611410382]
#         ,["CHF",1990,0.719968083]
#         ,["CHF",1991,0.697523728]
#         ,["CHF",1992,0.711414334]
#         ,["CHF",1993,0.676842046]
#         ,["CHF",1994,0.731272328]
#         ,["CHF",1995,0.845923023]
#         ,["CHF",1996,0.809151422]
#         ,["CHF",1997,0.689140153]
#         ,["CHF",1998,0.689813937]
#         ,["CHF",1999,0.665732958]
#         ,["CHF",2000,0.592212696]
#         ,["CHF",2001,0.592668198]
#         ,["CHF",2002,0.641678813]
#         ,["CHF",2003,0.742731287]
#         ,["CHF",2004,0.804217587]
#         ,["CHF",2005,0.803193235]
#         ,["CHF",2006,0.797602309]
#         ,["CHF",2007,0.833133816]
#         ,["CHF",2008,0.925566289]
#         ,["CHF",2009,0.921177644]
#         ,["CHF",2010,0.95885936]
#         ,["CHF",2011,1.126074277]
#         ,["CHF",2012,1.066457035]
#         ,["CHF",2013,1.07886084]
#         ,["CHF",2014,1.091523697]
#         ,["CHF",2015,1.039089418]
#         ,["CHF",2016,1.01498266]
#         ,["CHF",2017,1.020639364]
#         ,["CHF",2018,1.038411784]
#         ,["CHF",2019,1.043487965]
#         ,["CHF",2020,1.045613409]
#         ,["CHF",2021,1.04534651]
#         ,["CHF",2022,1.044373164]
#         ,["GBP",1980,2.32628255]
#         ,["GBP",1981,2.027903422]
#         ,["GBP",1982,1.750519422]
#         ,["GBP",1983,1.516993365]
#         ,["GBP",1984,1.336335286]
#         ,["GBP",1985,1.296331166]
#         ,["GBP",1986,1.467005831]
#         ,["GBP",1987,1.638903042]
#         ,["GBP",1988,1.781361189]
#         ,["GBP",1989,1.639704073]
#         ,["GBP",1990,1.784712982]
#         ,["GBP",1991,1.769367857]
#         ,["GBP",1992,1.765524745]
#         ,["GBP",1993,1.502019263]
#         ,["GBP",1994,1.531605042]
#         ,["GBP",1995,1.578466878]
#         ,["GBP",1996,1.561740396]
#         ,["GBP",1997,1.637694852]
#         ,["GBP",1998,1.656412066]
#         ,["GBP",1999,1.618224548]
#         ,["GBP",2000,1.516105186]
#         ,["GBP",2001,1.439964304]
#         ,["GBP",2002,1.501258685]
#         ,["GBP",2003,1.634373725]
#         ,["GBP",2004,1.831799852]
#         ,["GBP",2005,1.820401071]
#         ,["GBP",2006,1.842629791]
#         ,["GBP",2007,2.001679415]
#         ,["GBP",2008,1.853244234]
#         ,["GBP",2009,1.564477883]
#         ,["GBP",2010,1.546113395]
#         ,["GBP",2011,1.603604799]
#         ,["GBP",2012,1.585306416]
#         ,["GBP",2013,1.564467053]
#         ,["GBP",2014,1.647422194]
#         ,["GBP",2015,1.528959574]
#         ,["GBP",2016,1.35550518]
#         ,["GBP",2017,1.278857098]
#         ,["GBP",2018,1.285666251]
#         ,["GBP",2019,1.275525123]
#         ,["GBP",2020,1.263879967]
#         ,["GBP",2021,1.25191965]
#         ,["GBP",2022,1.240450746]
#         ,["USD",1980,1]
#         ,["USD",1981,1]
#         ,["USD",1982,1]
#         ,["USD",1983,1]
#         ,["USD",1984,1]
#         ,["USD",1985,1]
#         ,["USD",1986,1]
#         ,["USD",1987,1]
#         ,["USD",1988,1]
#         ,["USD",1989,1]
#         ,["USD",1990,1]
#         ,["USD",1991,1]
#         ,["USD",1992,1]
#         ,["USD",1993,1]
#         ,["USD",1994,1]
#         ,["USD",1995,1]
#         ,["USD",1996,1]
#         ,["USD",1997,1]
#         ,["USD",1998,1]
#         ,["USD",1999,1]
#         ,["USD",2000,1]
#         ,["USD",2001,1]
#         ,["USD",2002,1]
#         ,["USD",2003,1]
#         ,["USD",2004,1]
#         ,["USD",2005,1]
#         ,["USD",2006,1]
#         ,["USD",2007,1]
#         ,["USD",2008,1]
#         ,["USD",2009,1]
#         ,["USD",2010,1]
#         ,["USD",2011,1]
#         ,["USD",2012,1]
#         ,["USD",2013,1]
#         ,["USD",2014,1]
#         ,["USD",2015,1]
#         ,["USD",2016,1]
#         ,["USD",2017,1]
#         ,["USD",2018,1]
#         ,["USD",2019,1]
#         ,["USD",2020,1]
#         ,["USD",2021,1]
#         ,["USD",2022,1]
#         ,["XDR",1980,0]
#         ,["XDR",1981,0.849669143469742]
#         ,["XDR",1982,0.90850396994157]
#         ,["XDR",1983,0.936560463803807]
#         ,["XDR",1984,0.977321368541818]
#         ,["XDR",1985,0.986526268376143]
#         ,["XDR",1986,0.852142740302318]
#         ,["XDR",1987,0.773748051413953]
#         ,["XDR",1988,0.745580463328756]
#         ,["XDR",1989,0.780900616554035]
#         ,["XDR",1990,0.737135139084993]
#         ,["XDR",1991,0.732009701618817]
#         ,["XDR",1992,0.710154778497163]
#         ,["XDR",1993,0.716315481224692]
#         ,["XDR",1994,0.698574243263243]
#         ,["XDR",1995,0.659838749816477]
#         ,["XDR",1996,0.688776789706606]
#         ,["XDR",1997,0.726835133445115]
#         ,["XDR",1998,0.736969367894835]
#         ,["XDR",1999,0.731386642426741]
#         ,["XDR",2000,0.758990483529119]
#         ,["XDR",2001,0.78397183671084]
#         ,["XDR",2002,0.773218029400951]
#         ,["XDR",2003,0.713999836682518]
#         ,["XDR",2004,0.675328632803338]
#         ,["XDR",2005,0.677590113176999]
#         ,["XDR",2006,0.679903131283383]
#         ,["XDR",2007,0.653823023719494]
#         ,["XDR",2008,0.635019891904316]
#         ,["XDR",2009,0.649513668666035]
#         ,["XDR",2010,0.655705876546852]
#         ,["XDR",2011,0.633741293318671]
#         ,["XDR",2012,0.653151813755797]
#         ,["XDR",2013,0.658074196835493]
#         ,["XDR",2014,0.658697092781393]
#         ,["XDR",2015,0.714973903217865]
#         ,["XDR",2016,0.719540519400187]
#         ,["XDR",2017,0.722092665254238]
#         ,["XDR",2018,0]
#         ,["XDR",2019,0]
#         ,["XDR",2020,0]
#         ,["XDR",2021,0]
#         ,["XDR",2022,0]
#     ]
# )
# 
# ratedf.columns = ["currency","year","rate"]
        
recipient_dictionary = {
    "88":"ex-yugoslavia"
    ,"89":"europe"
    ,"189":"north-of-sahara"
    ,"289":"south-of-sahara"
    ,"298":"africa"
    ,"380":"west-indies"
    ,"389":"north-central-america"
    ,"489":"south-america"
    ,"498":"america"
    ,"589":"middle-east"
    ,"619":"central-asia"
    ,"679":"south-asia"
    ,"689":"south-central-asia"
    ,"789":"east-asia"
    ,"798":"asia"
    ,"889":"oceania"
    ,"998":"bilateral-unspecified"
    ,"AE":"AE"
    ,"AF":"AF"
    ,"AG":"AG"
    ,"AI":"AI"
    ,"AL":"AL"
    ,"AM":"AM"
    ,"AN":"ANHH"
    ,"AO":"AO"
    ,"AR":"AR"
    ,"AW":"AW"
    ,"AZ":"AZ"
    ,"BA":"BA"
    ,"BB":"BB"
    ,"BD":"BD"
    ,"BF":"BF"
    ,"BG":"BG"
    ,"BH":"BH"
    ,"BI":"BI"
    ,"BJ":"BJ"
    ,"BM":"BM"
    ,"BN":"BN"
    ,"BO":"BO"
    ,"BR":"BR"
    ,"BS":"BS"
    ,"BT":"BT"
    ,"BW":"BW"
    ,"BY":"BY"
    ,"BZ":"BZ"
    ,"CD":"CD"
    ,"CF":"CF"
    ,"CG":"CG"
    ,"CI":"CI"
    ,"CK":"CK"
    ,"CL":"CL"
    ,"CM":"CM"
    ,"CN":"CN"
    ,"CO":"CO"
    ,"CR":"CR"
    ,"CU":"CU"
    ,"CV":"CV"
    ,"CY":"CY"
    ,"CZ":"CZ"
    ,"DJ":"DJ"
    ,"DM":"DM"
    ,"DO":"DO"
    ,"DZ":"DZ"
    ,"EC":"EC"
    ,"EE":"EE"
    ,"EG":"EG"
    ,"ER":"ER"
    ,"ET":"ET"
    ,"FJ":"FJ"
    ,"FK":"FK"
    ,"FM":"FM"
    ,"GA":"GA"
    ,"GD":"GD"
    ,"GE":"GE"
    ,"GH":"GH"
    ,"GI":"GI"
    ,"GM":"GM"
    ,"GN":"GN"
    ,"GQ":"GQ"
    ,"GT":"GT"
    ,"GW":"GW"
    ,"GY":"GY"
    ,"HK":"HK"
    ,"HN":"HN"
    ,"HR":"HR"
    ,"HT":"HT"
    ,"HU":"HU"
    ,"ID":"ID"
    ,"IL":"IL"
    ,"IN":"IN"
    ,"IQ":"IQ"
    ,"IR":"IR"
    ,"JM":"JM"
    ,"JO":"JO"
    ,"KE":"KE"
    ,"KG":"KG"
    ,"KH":"KH"
    ,"KI":"KI"
    ,"KM":"KM"
    ,"KN":"KN"
    ,"KP":"KP"
    ,"KR":"KR"
    ,"KW":"KW"
    ,"KY":"KY"
    ,"KZ":"KZ"
    ,"LA":"LA"
    ,"LB":"LB"
    ,"LC":"LC"
    ,"LK":"LK"
    ,"LR":"LR"
    ,"LS":"LS"
    ,"LT":"LT"
    ,"LV":"LV"
    ,"LY":"LY"
    ,"MA":"MA"
    ,"MD":"MD"
    ,"ME":"ME"
    ,"MG":"MG"
    ,"MH":"MH"
    ,"MK":"MK"
    ,"ML":"ML"
    ,"MM":"MM"
    ,"MN":"MN"
    ,"MO":"MO"
    ,"MP":"MP"
    ,"MR":"MR"
    ,"MS":"MS"
    ,"MT":"MT"
    ,"MU":"MU"
    ,"MV":"MV"
    ,"MW":"MW"
    ,"MX":"MX"
    ,"MY":"MY"
    ,"MZ":"MZ"
    ,"NA":"NA"
    ,"NC":"NC"
    ,"NE":"NE"
    ,"NG":"NG"
    ,"NI":"NI"
    ,"NP":"NP"
    ,"NR":"NR"
    ,"NU":"NU"
    ,"OM":"OM"
    ,"PA":"PA"
    ,"PE":"PE"
    ,"PF":"PF"
    ,"PG":"PG"
    ,"PH":"PH"
    ,"PK":"PK"
    ,"PL":"PL"
    ,"PS":"PS"
    ,"PW":"PW"
    ,"PY":"PY"
    ,"QA":"QA"
    ,"RO":"RO"
    ,"RS":"RS"
    ,"RU":"RU"
    ,"RW":"RW"
    ,"SA":"SA"
    ,"SB":"SB"
    ,"SC":"SC"
    ,"SD":"SD"
    ,"SG":"SG"
    ,"SH":"SH"
    ,"SI":"SI"
    ,"SK":"SK"
    ,"SL":"SL"
    ,"SN":"SN"
    ,"SO":"SO"
    ,"SR":"SR"
    ,"SS":"SS"
    ,"ST":"ST"
    ,"SV":"SV"
    ,"SY":"SY"
    ,"SZ":"SZ"
    ,"TC":"TC"
    ,"TD":"TD"
    ,"TG":"TG"
    ,"TH":"TH"
    ,"TJ":"TJ"
    ,"TK":"TK"
    ,"TL":"TL"
    ,"TM":"TM"
    ,"TN":"TN"
    ,"TO":"TO"
    ,"TR":"TR"
    ,"TT":"TT"
    ,"TV":"TV"
    ,"TW":"TW"
    ,"TZ":"TZ"
    ,"UA":"UA"
    ,"UG":"UG"
    ,"UY":"UY"
    ,"UZ":"UZ"
    ,"VC":"VC"
    ,"VE":"VE"
    ,"VG":"VG"
    ,"VN":"VN"
    ,"VU":"VU"
    ,"WF":"WF"
    ,"WS":"WS"
    ,"XK":"XK"
    ,"YE":"YE"
    ,"YT":"YT"
    ,"ZA":"ZA"
    ,"ZM":"ZM"
    ,"ZW":"ZW"
}

# def make_versioned_code_dict(version):
#     if version in ["1.01","1.02","1.03"]:
#         version = "1.04"
#     master_dict = {}
#     desired_lists = ["TransactionType","Currency","Sector","Country","Region","DisbursementChannel","FinanceType","AidType"]
#     for desired_list in desired_lists:
#         codelist = iati.default.codelist(desired_list,version)
#         master_dict[desired_list] = {code.value:code.name for code in codelist.codes}
#     if version in ['1.04','1.05']:
#         master_dict["TransactionType"] = {
#             "QP":"Purchase of Equity"
#             ,"C":"Commitment"
#             ,"E":"Expenditure"
#             ,"D":"Disbursement"
#             ,"IR":"Interest Repayment"
#             ,"CG":"Credit Guarantee"
#             ,"QS":"Sale of Equity"
#             ,"R":"Reimbursement"
#             ,"LR":"Loan Repayment"
#             ,"IF":"Incoming Funds"
#         }
#     return master_dict

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
                
        #If percentages are greater than 100, rescale to 100. Also divide by 100 to make sure percentages run 0 to 1.00
        activity_sector_percentage = max(activity_sector_percentage,100.0)
        activity_recipient_percentage = max(activity_recipient_percentage,100.0)
        
        for activity_sector_code in activity_sectors:
            activity_sectors[activity_sector_code] = (activity_sectors[activity_sector_code] / activity_sector_percentage) if (activity_sectors[activity_sector_code]) is not None else None
        for activity_recipient_code in activity_recipients:
            activity_recipients[activity_recipient_code] = (activity_recipients[activity_recipient_code] / activity_recipient_percentage) if (activity_recipients[activity_recipient_code]) is not None else None
                
        #If there's only one recipient or sector, it's percent is implied to be 100
        if len(activity_sectors.keys())==1:
            activity_sectors[activity_sectors.keys()[0]] = 1
        if len(activity_recipients.keys())==1:
            activity_recipients[activity_recipients.keys()[0]] = 1
        
        has_transactions = "transaction" in child_tags
        if has_transactions:
            transactions = activity.findall("transaction")
            #Once through the transactions to find the sector sum, sector percents, recipient sum, recipient percents
            transaction_sectors = {}
            transaction_recipients = {}
            for transaction in transactions:
                transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                if transaction_type_code in ["E","D","3","4"]:
                    sector_code = default_first(transaction.xpath("sector/@code"))
                    sector_vocabulary = default_first(transaction.xpath("sector/@vocabulary"))
                    sector_code = sector_code if sector_vocabulary in ["","1","2","DAC","DAC-3"] else None
                    
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
                    
            #If we turned up valid sectors/recipients, don't use the activity-level ones
            use_activity_sectors = len(transaction_sectors.keys())==0
            use_activity_recipients = len(transaction_recipients.keys())==0
            
            #Calc the sum of non-negative sectors
            transaction_sector_value_sum = 0.0
            for sector_code in transaction_sectors:
                transaction_sector_value_sum += transaction_sectors[sector_code] if (transaction_sectors[sector_code]>0) else 0.0
            if transaction_sector_value_sum > 0.0:
                for sector_code in transaction_sectors:    
                    transaction_sectors[sector_code] = transaction_sectors[sector_code]/transaction_sector_value_sum
                
            transaction_recipient_value_sum = 0.0
            for recipient_code in transaction_recipients:
                transaction_recipient_value_sum += transaction_recipients[recipient_code] if (transaction_recipients[recipient_code]>0.0) else 0.0
            if transaction_recipient_value_sum > 0.0:
                for recipient_code in transaction_recipients:
                    transaction_recipients[recipient_code] = transaction_recipients[recipient_code]/transaction_recipient_value_sum
                        
            #If there's only one recipient or sector, it's percent is implied to be 100
            if len(transaction_sectors.keys())==1:
                transaction_sectors[transaction_sectors.keys()[0]] = 1
            if len(transaction_recipients.keys())==1:
                transaction_recipients[transaction_recipients.keys()[0]] = 1
                    
            #Another time through
            for transaction in transactions:
                transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                if transaction_type_code in ["E","D","3","4"]:
                    transaction_date = default_first(transaction.xpath("transaction-date/@iso-date"))
                    year = int(transaction_date[:4]) if transaction_date is not None else None
                    
                    currency = default_first(transaction.xpath("value/@currency"))
                    currency = replace_default_if_none(currency,defaults["default-currency"])
        
                    value = default_first(transaction.xpath("value/text()"))
                    try:
                        value = float(value.replace(" ", "")) if value is not None else None
                    except ValueError:
                        value = None
                    value_date = default_first(transaction.xpath("value/@value-date"))
                    
                    sector_code = default_first(transaction.xpath("sector/@code"))                
                    
                    recipient_code = default_first(transaction.xpath("recipient-country/@code"))
                    recipient_code = replace_default_if_none(recipient_code,default_first(transaction.xpath("recipient-region/@code")))
                    
                    flow_type_code = default_first(transaction.xpath("flow-type/@code"))
                    flow_type_code = replace_default_if_none(flow_type_code,defaults["default-flow-type"])
                        
                    disbursement_channel_code = default_first(transaction.xpath("disbursement-channel/@code"))
                    
                    finance_type_code = default_first(transaction.xpath("finance-type/@code"))
                    finance_type_code = replace_default_if_none(finance_type_code,defaults["default-finance-type"])
                    
                    aid_type_code = default_first(transaction.xpath("aid-type/@code"))
                    aid_type_code = replace_default_if_none(aid_type_code,defaults["default-aid-type"])
                    
                    category = None
                    budget_type = None
                    b_or_t = "Transaction"
                    
                    if value>0:
                        if use_activity_recipients:
                            if use_activity_sectors:
                                #Activity recipients and sectors
                                for activity_recipient_code in activity_recipients.keys():
                                    activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                    for activity_sector_code in activity_sectors.keys():
                                        activity_sector_percentage = activity_sectors[activity_sector_code]
                                        calculated_value = value*activity_recipient_percentage*activity_sector_percentage if (activity_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                        recip = recode_if_not_none(activity_recipient_code,recipient_dictionary)
                                        sec_code = activity_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        # row = [version,iati_identifier,secondary_reporter,transaction_type_code,year,transaction_date,recip,flow_type_code,category,finance_type_code,aid_type_code,currency,converted_value,short_description,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type]
                                        row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                        output.append(row)
                            else:
                                #Just activity recipients
                                for activity_recipient_code in activity_recipients.keys():
                                    activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                    calculated_value = value*activity_recipient_percentage if (activity_recipient_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                    recip = recode_if_not_none(activity_recipient_code,recipient_dictionary)
                                    sec_code = sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                    output.append(row)
                        else:
                            if use_activity_sectors:
                                #Just activity sectors
                                for activity_sector_code in activity_sectors.keys():
                                    activity_sector_percentage = activity_sectors[activity_sector_code]
                                    calculated_value = value*activity_sector_percentage if (activity_sector_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                    recip = recode_if_not_none(recipient_code,recipient_dictionary)
                                    sec_code = activity_sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                    output.append(row)
                            else:
                                #Neither activity recipients nor sectors
                                converted_value = convert_usd(value,year,currency,ratedf)
                                recip = recode_if_not_none(recipient_code,recipient_dictionary)
                                sec_code = sector_code
                                pur_code = sec_code[:3] if sec_code is not None else None
                                row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                output.append(row)
                
            has_budget = "budget" in child_tags
            if has_budget:
                budgets = activity.findall("budget")
                for budget in budgets:
                    transaction_type_code = None
                    if "type" in budget.attrib.keys():
                        budget_type = budget.attrib["type"]
                    else:
                        budget_type = None
                        
                    transaction_date = default_first(budget.xpath("period-start/@iso-date"))
                    year = int(transaction_date[:4]) if transaction_date is not None else None
                        
                    value = default_first(budget.xpath("value/text()"))
                    try:
                        value = float(value.replace(" ", "")) if value is not None else None
                    except ValueError:
                        value = None
                    value_date = default_first(budget.xpath("value/@value-date"))
                    currency = default_first(budget.xpath("value/@currency"))
                    currency = replace_default_if_none(currency,defaults["default-currency"])
                    
                    flow_type_code = defaults["default-flow-type"]
                    
                    finance_type_code = defaults["default-finance-type"]
                    
                    aid_type_code = defaults["default-aid-type"]
                    
                    category = None
                    disbursement_channel_code = None
                    b_or_t = "Budget"
            
                    if value>0:
                        if use_activity_recipients:
                            if use_activity_sectors:
                                #Activity recipients and sectors
                                for activity_recipient_code in activity_recipients.keys():
                                    activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                    for activity_sector_code in activity_sectors.keys():
                                        activity_sector_percentage = activity_sectors[activity_sector_code]
                                        calculated_value = value*activity_recipient_percentage*activity_sector_percentage if (activity_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                        recip = recode_if_not_none(activity_recipient_code,recipient_dictionary)
                                        sec_code = activity_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                        output.append(row)
                            else:
                                #Just activity recipients
                                for activity_recipient_code in activity_recipients.keys():
                                    activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                    for transaction_sector_code in transaction_sectors.keys():
                                        transaction_sector_percentage = transaction_sectors[transaction_sector_code]
                                        calculated_value = value*activity_recipient_percentage*transaction_sector_percentage if (activity_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                        recip = recode_if_not_none(activity_recipient_code,recipient_dictionary)
                                        sec_code = transaction_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                        output.append(row)
                        else:
                            if use_activity_sectors:
                                #Just activity sectors
                                for transaction_recipient_code in transaction_recipients.keys():
                                    transaction_recipient_percentage = transaction_recipients[transaction_recipient_code]
                                    for activity_sector_code in activity_sectors.keys():
                                        activity_sector_percentage = activity_sectors[activity_sector_code]
                                        calculated_value = value*transaction_recipient_percentage*activity_sector_percentage if (transaction_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                        recip = recode_if_not_none(transaction_recipient_code,recipient_dictionary)
                                        sec_code = activity_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                        output.append(row)
                            else:
                                #Neither activity recipients nor sectors
                                for transaction_recipient_code in transaction_recipients.keys():
                                    transaction_recipient_percentage = transaction_recipients[transaction_recipient_code]
                                    for transaction_sector_code in transaction_sectors.keys():
                                        transaction_sector_percentage = transaction_sectors[transaction_sector_code]
                                        calculated_value = value*transaction_recipient_percentage*transaction_sector_percentage if (transaction_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,ratedf)
                                        recip = recode_if_not_none(transaction_recipient_code,recipient_dictionary)
                                        sec_code = transaction_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier]
                                        output.append(row)
    return output
    
if __name__ == '__main__':
    
    shutil.rmtree("C:/Users/Alex/Documents/Data/IATI/sep/")
    os.mkdir("C:/Users/Alex/Documents/Data/IATI/sep/")
    
    
    rootdir = 'C:/Users/Alex/Documents/Data/IATI-Registry-Refresher/data'
    header = ["year","recipient_code","flow_code","category","finance_type","aid_type","usd_disbursement","short_description","purpose_code","sector_code","channel_code","long_description","ftc","pba","budget_or_transaction","budget_type","iati_identifier"]
    
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
    full_header = ["year","recipient_code","flow_code","category","finance_type","aid_type","usd_disbursement","short_description","purpose_code","sector_code","channel_code","long_description","ftc","pba","budget_or_transaction","budget_type","iati_identifier","donor_code"]
    header_frame = pd.DataFrame([full_header])
    header_frame.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/000header.csv",index=False,header=False,encoding="utf-8")
    
    for subdir, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(subdir,filename)
            publisher = os.path.basename(subdir)
            if publisher in donor_code_lookup.keys():
            # if publisher in sorted(donor_code_lookup.keys())[57:]:
                print filename
                try:
                    root = etree.parse(filepath).getroot()
                except etree.XMLSyntaxError:
                    continue
                output = flatten_activities(root)
                if len(output)>0:
                    data = pd.DataFrame(output)
                    data.columns = header
                    # data['publisher'] = publisher
                    data['donor_code'] = donor_code_lookup[publisher]
                    data.to_csv("C:/Users/Alex/Documents/Data/IATI/sep/{}.csv".format(filename),index=False,header=False,encoding="utf-8")
                    
    os.system("cat C:/Users/Alex/Documents/Data/IATI/sep/*.csv > C:/Users/Alex/Documents/Data/IATI/iati.csv")