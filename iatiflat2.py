import progressbar
from lxml import etree
import datetime
import dateutil
import pdb

#Two dimension exchange rate dictionary. Access exchange rates by currency and year like ratedf[currencyCode][year]
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
        
#Dictionary to translate between DAC recipient code (as reported in IATI) to CRS recipient code
recipient_dictionary = {
    "88":"88"
    ,"89":"89"
    ,"189":"189"
    ,"289":"289"
    ,"298":"298"
    ,"380":"380"
    ,"389":"389"
    ,"489":"489"
    ,"498":"498"
    ,"589":"589"
    ,"619":"619"
    ,"679":"679"
    ,"689":"689"
    ,"789":"789"
    ,"798":"798"
    ,"889":"889"
    ,"998":"998"
    ,"AE":"576"
    ,"AF":"625"
    ,"AG":"377"
    ,"AI":"376"
    ,"AL":"71"
    ,"AM":"610"
    ,"AN":"361"
    ,"AO":"225"
    ,"AR":"425"
    ,"AW":"373"
    ,"AZ":"611"
    ,"BA":"64"
    ,"BB":"329"
    ,"BD":"666"
    ,"BF":"287"
    ,"BG":"72"
    ,"BH":"530"
    ,"BI":"228"
    ,"BJ":"236"
    ,"BM":"331"
    ,"BN":"725"
    ,"BO":"428"
    ,"BR":"431"
    ,"BS":"328"
    ,"BT":"630"
    ,"BW":"227"
    ,"BY":"86"
    ,"BZ":"352"
    ,"CD":"235"
    ,"CF":"231"
    ,"CG":"234"
    ,"CI":"247"
    ,"CK":"831"
    ,"CL":"434"
    ,"CM":"229"
    ,"CN":"730"
    ,"CO":"437"
    ,"CR":"336"
    ,"CU":"338"
    ,"CV":"230"
    ,"CY":"30"
    ,"CZ":"68"
    ,"DJ":"274"
    ,"DM":"378"
    ,"DO":"340"
    ,"DZ":"130"
    ,"EC":"440"
    ,"EE":"82"
    ,"EG":"142"
    ,"ER":"271"
    ,"ET":"238"
    ,"FJ":"832"
    ,"FK":"443"
    ,"FM":"860"
    ,"GA":"239"
    ,"GD":"381"
    ,"GE":"612"
    ,"GH":"241"
    ,"GI":"35"
    ,"GM":"240"
    ,"GN":"243"
    ,"GQ":"245"
    ,"GT":"347"
    ,"GW":"244"
    ,"GY":"446"
    ,"HK":"735"
    ,"HN":"351"
    ,"HR":"62"
    ,"HT":"349"
    ,"HU":"75"
    ,"ID":"738"
    ,"IL":"546"
    ,"IN":"645"
    ,"IQ":"543"
    ,"IR":"540"
    ,"JM":"354"
    ,"JO":"549"
    ,"KE":"248"
    ,"KG":"614"
    ,"KH":"728"
    ,"KI":"836"
    ,"KM":"233"
    ,"KN":"382"
    ,"KP":"740"
    ,"KR":"742"
    ,"KW":"552"
    ,"KY":"386"
    ,"KZ":"613"
    ,"LA":"745"
    ,"LB":"555"
    ,"LC":"383"
    ,"LK":"640"
    ,"LR":"251"
    ,"LS":"249"
    ,"LT":"84"
    ,"LV":"83"
    ,"LY":"133"
    ,"MA":"136"
    ,"MD":"93"
    ,"ME":"65"
    ,"MG":"252"
    ,"MH":"859"
    ,"MK":"66"
    ,"ML":"255"
    ,"MM":"635"
    ,"MN":"753"
    ,"MO":"748"
    ,"MP":"858"
    ,"MR":"256"
    ,"MS":"385"
    ,"MT":"45"
    ,"MU":"257"
    ,"MV":"655"
    ,"MW":"253"
    ,"MX":"358"
    ,"MY":"751"
    ,"MZ":"259"
    ,"NA":"275"
    ,"NC":"850"
    ,"NE":"260"
    ,"NG":"261"
    ,"NI":"364"
    ,"NP":"660"
    ,"NR":"845"
    ,"NU":"856"
    ,"OM":"558"
    ,"PA":"366"
    ,"PE":"454"
    ,"PF":"840"
    ,"PG":"862"
    ,"PH":"755"
    ,"PK":"665"
    ,"PL":"76"
    ,"PS":"550"
    ,"PW":"861"
    ,"PY":"451"
    ,"QA":"561"
    ,"RO":"77"
    ,"RS":"63"
    ,"RU":"87"
    ,"RW":"266"
    ,"SA":"566"
    ,"SB":"866"
    ,"SC":"270"
    ,"SD":"278"
    ,"SG":"761"
    ,"SH":"276"
    ,"SI":"61"
    ,"SK":"69"
    ,"SL":"272"
    ,"SN":"269"
    ,"SO":"273"
    ,"SR":"457"
    ,"SS":"279"
    ,"ST":"268"
    ,"SV":"342"
    ,"SY":"573"
    ,"SZ":"280"
    ,"TC":"387"
    ,"TD":"232"
    ,"TG":"283"
    ,"TH":"764"
    ,"TJ":"615"
    ,"TK":"868"
    ,"TL":"765"
    ,"TM":"616"
    ,"TN":"139"
    ,"TO":"870"
    ,"TR":"55"
    ,"TT":"375"
    ,"TV":"872"
    ,"TW":"732"
    ,"TZ":"282"
    ,"UA":"85"
    ,"UG":"285"
    ,"UY":"460"
    ,"UZ":"617"
    ,"VC":"384"
    ,"VE":"463"
    ,"VG":"388"
    ,"VN":"769"
    ,"VU":"854"
    ,"WF":"876"
    ,"WS":"880"
    ,"XK":"57"
    ,"YE":"580"
    ,"YT":"258"
    ,"ZA":"218"
    ,"ZM":"288"
    ,"ZW":"265"
}

#Dictionary that translates between iati donor code and CRS donor code
donor_code_lookup = {
    "af":"1012"
    ,"afd":"4"
    ,"afdb":"913"
    ,"aics":"6"
    ,"asdb":"915"
    ,"ausgov":"801"
    ,"be-dgd":"2"
    ,"bmgf":"1601"
    ,"bmz":"5"
    ,"btc-ctb":"2"
    ,"cdc":"12"
    ,"cif":"1011"
    ,"danida":"3"
    ,"deccadmin":"12"
    ,"defra_transparency":"12"
    ,"dfid":"12"
    ,"doh":"12"
    ,"dwp":"12"
    ,"ebrd":"990"
    ,"ec-devco":"918"
    ,"ec-echo":"918"
    ,"ec-fpi":"918"
    ,"ec-near":"918"
    ,"eib":"918"
    ,"fao":"932"
    ,"fco":"12"
    ,"finance_canada":"301"
    ,"finland_mfa":"18"
    ,"gac-amc":"301"
    ,"gain":"1311"
    ,"gavi":"1311"
    ,"hooda":"12"
    ,"iadb":"909"
    ,"idrccrdi":"301"
    ,"ifad":"988"
    ,"ifcwbg":"903"
    ,"ilo":"940"
    ,"irishaid":"21"
    ,"jica":"701"
    ,"lithuania_mfa":"84"
    ,"maec":"50"
    ,"mfat":"820"
    ,"minbuza_nl":"7"
    ,"mrc":"12"
    ,"norad":"8"
    ,"odakorea":"742"
    ,"ofid":"951"
    ,"scottish_government":"12"
    ,"sdc_ch":"11"
    ,"sida":"10"
    ,"slovakaid":"69"
    ,"theglobalfund":"1312"
    ,"uasd":"77"
    ,"ukmod":"12"
    ,"unaids":"971"
    ,"undp":"959"
    ,"unfpa":"974"
    ,"unicef":"963"
    ,"unitedstates":"302"
    ,"usaid":"302"
    ,"wfa":"12"
    ,"wfp":"966"
    ,"who":"928"
    ,"worldbank":"905"
}
#And a further dictionary to translate between CRS donor code and our internal entity identifier
donor_di_code_lookup = {
    "1012":"adaptation-fund"
    ,"913":"afdb"
    ,"915":"asdb"
    ,"801":"AU"
    ,"2":"BE"
    ,"1601":"bmgf"
    ,"301":"CA"
    ,"11":"CH"
    ,"1011":"cif"
    ,"5":"DE"
    ,"3":"DK"
    ,"990":"ebrd"
    ,"50":"ES"
    ,"918":"EU"
    ,"932":"fao"
    ,"18":"FI"
    ,"4":"FR"
    ,"1311":"gavi"
    ,"12":"GB"
    ,"1312":"global-fund"
    ,"905":"ida"
    ,"909":"idb"
    ,"21":"IE"
    ,"988":"ifad"
    ,"903":"ifc"
    ,"940":"international-labour-organisation"
    ,"6":"IT"
    ,"701":"JP"
    ,"742":"KR"
    ,"84":"LT"
    ,"7":"NL"
    ,"8":"NO"
    ,"820":"NZ"
    ,"951":"ofid"
    ,"77":"RO"
    ,"10":"SE"
    ,"69":"SK"
    ,"971":"unaids"
    ,"959":"undp"
    ,"974":"unfpa"
    ,"963":"unicef"
    ,"302":"US"
    ,"966":"wfp"
    ,"928":"who"
}

#Used for ambiguously structed arrays resulting from XML queries. If an array has any entries, take the first one.
def default_first(array):
    #If an array isn't empty, give us the first element
    return array[0] if array is not None and len(array)>0 else None

#Used for ambiguous result default replacement. If value doesn't exist, replace it with the default.
def replace_default_if_none(value,default):
    if value is None:
        return default
    elif str.strip(value) == "":
        return default
    else:
        return value
    
#Used for ambiguous recoding. If code exists, try and use the dictionary to look up the result.
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

#Used for currency conversion. Works like recode_if_not_none but for our 2-dimension exchange rate dictionary
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

#A class that will hold the flattening function and dictionary definitions
class IatiFlat(object):
    def __init__(self):
        self.header = ["year","recipient_code","to_di_id","flow_code","category","finance_type","aid_type","usd_disbursement","short_description","purpose_code","sector_code","channel_code","long_description","ftc","pba","budget_or_transaction","budget_type","iati_identifier","incoming"]
        self.dictionaries = {}
        #Defaults, can be overwritten with next function
        self.dictionaries["ratedf"] = ratedf
        self.dictionaries["recipient_dictionary"] = recipient_dictionary
        self.dictionaries["donor_code_lookup"] = donor_code_lookup
        self.dictionaries["donor_di_code_lookup"] = donor_di_code_lookup
    def define_dict(self,name,dictionary):
        self.dictionaries[name] = dictionary
    #Main flattening function here. Input is the XML root of the XML document, and output is an array of arrays with flattened data.
    def flatten_activities(self,root):
        for dictionary_name in ["ratedf","recipient_dictionary"]:
            assert dictionary_name in self.dictionaries, "Missing dictionary: {}".format(dictionary_name)
        output = []
        try:
            version = root.attrib["version"]
        except KeyError:
            #Defaults to 2.02 if  the document happens to be missing an IATI version
            version = '2.02'
        
        #Find all activities
        activity_len = len(root.findall("iati-activity"))
            
        #Set up a quick progress bar for tracking processing; iterate through every activity
        bar = progressbar.ProgressBar()
        for i in bar(range(0,activity_len)):
            activity = root.xpath('iati-activity[%s]' % (i + 1) )[0]
            #Capture iati identifier
            iati_identifier = default_first(activity.xpath("iati-identifier/text()"))
            
                
            child_tags = [child.tag for child in activity.getchildren()]
    
            #Not used, since we're filtering for the donors we want anyway.
            # secondary_reporter = default_first(activity.xpath("reporting-org/@secondary-reporter"))
            # secondary_reporter = replace_default_if_none(secondary_reporter,"0")
            
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
                    
            #For every sector and every recipient in the activity, try and total the percentage splits
            activity_sector_percentage = 0.0
            activity_recipient_percentage = 0.0
            
            sectors = activity.findall("sector")
            activity_sectors = {}
            for sector in sectors:
                attribs = sector.attrib
                attrib_keys = attribs.keys()
                percentage = attribs['percentage'] if 'percentage' in attrib_keys else None
                if percentage is not None:
                    percentage = percentage.replace("%","")
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
                if percentage is not None:
                    percentage = percentage.replace("%","")
                activity_recipient_percentage += float(percentage) if percentage is not None else 0.0
                code = attribs['code'] if 'code' in attrib_keys else None
                if code is not None:
                    activity_recipients[code] = float(percentage) if percentage is not None else None
                
            recipient_regions = activity.findall("recipient-region")
            for recipient_region in recipient_regions:
                attribs = recipient_region.attrib
                attrib_keys = attribs.keys()
                percentage = attribs['percentage'] if 'percentage' in attrib_keys else None
                if percentage is not None:
                    percentage = percentage.replace("%","")
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
                    
                #Activity has any incoming funds
                incoming = False
                        
                #Another time through transactions to record data after sums are recorded
                for transaction in transactions:
                    transaction_type_code = default_first(transaction.xpath("transaction-type/@code"))
                    if transaction_type_code in ["IF","1","11"]:
                        incoming = True
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
                        
                        #Here's where the splitting happens. We're taking the boolean indicators on whether we're splitting by activity or transaction level percentages
                        #and looping through for-loops that add additional rows depending on the number of possible combinations.
                        #Final percentages are calculated as the intersectional percentages of sector and recipient. Important to note that missing data for either sectors
                        #or recipients will result in loss of valid value data.
                        if value>0:
                            if use_activity_recipients:
                                if use_activity_sectors:
                                    #Activity recipients and sectors
                                    for activity_recipient_code in activity_recipients.keys():
                                        activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                        for activity_sector_code in activity_sectors.keys():
                                            activity_sector_percentage = activity_sectors[activity_sector_code]
                                            calculated_value = value*activity_recipient_percentage*activity_sector_percentage if (activity_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                            converted_value = convert_usd(calculated_value,year,currency,self.dictionaries["ratedf"])
                                            recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                            to_di_id = activity_recipient_code
                                            sec_code = activity_sector_code
                                            pur_code = sec_code[:3] if sec_code is not None else None
                                            row = [year,recip,to_di_id,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier,incoming]
                                            output.append(row)
                                else:
                                    #Just activity recipients
                                    for activity_recipient_code in activity_recipients.keys():
                                        activity_recipient_percentage = activity_recipients[activity_recipient_code]
                                        calculated_value = value*activity_recipient_percentage if (activity_recipient_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,self.dictionaries["ratedf"])
                                        recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                        to_di_id = activity_recipient_code
                                        sec_code = sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,to_di_id,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier,incoming]
                                        output.append(row)
                            else:
                                if use_activity_sectors:
                                    #Just activity sectors
                                    for activity_sector_code in activity_sectors.keys():
                                        activity_sector_percentage = activity_sectors[activity_sector_code]
                                        calculated_value = value*activity_sector_percentage if (activity_sector_percentage is not None) else None
                                        converted_value = convert_usd(calculated_value,year,currency,self.dictionaries["ratedf"])
                                        recip = recode_if_not_none(recipient_code,self.dictionaries["recipient_dictionary"])
                                        to_di_id = recipient_code
                                        sec_code = activity_sector_code
                                        pur_code = sec_code[:3] if sec_code is not None else None
                                        row = [year,recip,to_di_id,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier,incoming]
                                        output.append(row)
                                else:
                                    #Neither activity recipients nor sectors
                                    converted_value = convert_usd(value,year,currency,self.dictionaries["ratedf"])
                                    recip = recode_if_not_none(recipient_code,self.dictionaries["recipient_dictionary"])
                                    to_di_id = recipient_code
                                    sec_code = sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [year,recip,to_di_id,flow_type_code,category,finance_type_code,aid_type_code,converted_value,short_description,pur_code,sec_code,channel_code,long_description,ftc,pba,b_or_t,budget_type,iati_identifier,incoming]
                                    output.append(row)
                    
                #Loop through budgets, and capture as close equivalents as we can to transactions
                budget_output = []
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
                        transaction_date_end = default_first(budget.xpath("period-end/@iso-date"))
                        time_range = {}
                        try:
                            time_range["start"] = dateutil.parser.parse(transaction_date)
                            time_range["end"] = dateutil.parser.parse(transaction_date_end)
                        except (TypeError,ValueError) as error:
                            time_range["start"] = None
                            time_range["end"] = None
                        if time_range["start"] is not None:
                            time_range["length"] = time_range["end"]-time_range["start"]
                            if time_range["length"]<datetime.timedelta(370):
                                year = time_range["start"].year
                                    
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
                                    budget_data = {
                                        "use_activity_recipients":use_activity_recipients
                                        ,"use_activity_sectors":use_activity_sectors
                                        ,"activity_recipients":activity_recipients
                                        ,"activity_sectors":activity_sectors
                                        ,"transaction_recipients":transaction_recipients
                                        ,"transaction_sectors":transaction_sectors
                                        ,"value":value
                                        ,"year":year
                                        ,"currency":currency
                                        ,"flow_type_code":flow_type_code
                                        ,"category":category
                                        ,"finance_type_code":finance_type_code
                                        ,"aid_type_code":aid_type_code
                                        ,"short_description":short_description
                                        ,"channel_code":channel_code
                                        ,"long_description":long_description
                                        ,"ftc":ftc
                                        ,"pba":pba
                                        ,"b_or_t":b_or_t
                                        ,"budget_type":budget_type
                                        ,"iati_identifier":iati_identifier
                                        ,"incoming":incoming
                                    }
                                    meta = {"time_range":time_range,"budget_type":budget_type,"data":budget_data}
                                    budget_output.append(meta)
                if len(budget_output)>1:
                    overlaps = []
                    spoiled = False
                    keep_indexes = range(0,len(budget_output))
                    #All possible combinations of 2
                    for i in range(0,len(budget_output)):
                        if i+1 < len(budget_output):
                            for j in range(i+1,len(budget_output)):
                                first_budget = budget_output[i]
                                second_budget = budget_output[j]
                                if second_budget["time_range"]["end"]<=first_budget["time_range"]["end"] and second_budget["time_range"]["end"]>=first_budget["time_range"]["start"]:
                                    overlaps.append((i,j))
                                    if i in keep_indexes:
                                        keep_indexes.remove(i)
                                    if j in keep_indexes:
                                        keep_indexes.remove(j)
                                elif second_budget["time_range"]["start"]>=first_budget["time_range"]["start"] and second_budget["time_range"]["start"]<=first_budget["time_range"]["end"]:
                                    overlaps.append((i,j))
                                    if i in keep_indexes:
                                        keep_indexes.remove(i)
                                    if j in keep_indexes:
                                        keep_indexes.remove(j)
                    if len(overlaps)>1:
                        for i, j in overlaps:
                            #If we've happened to put them back in the queue, take them out
                            if i in keep_indexes:
                                keep_indexes.remove(i)
                            if j in keep_indexes:
                                keep_indexes.remove(j)
                            budget1 = budget_output[i]
                            budget2 = budget_output[j]
                            #Only keep overlaps if one is revised and one is original
                            if budget1["budget_type"]=="1" and budget2["budget_type"]=="2":
                                keep_indexes.append(j)
                            elif budget1["budget_type"]=="2" and budget2["budget_type"]=="1":
                                keep_indexes.append(i)
                            elif budget1["budget_type"]==budget2["budget_type"]:
                                spoiled = True
                    if not spoiled:
                        for keep_index in keep_indexes:
                            vb = budget_output[keep_index]
                            if vb["data"]["use_activity_recipients"]:
                                if vb["data"]["use_activity_sectors"]:
                                    #Activity recipients and sectors
                                    for activity_recipient_code in vb["data"]["activity_recipients"].keys():
                                        activity_recipient_percentage = vb["data"]["activity_recipients"][activity_recipient_code]
                                        for activity_sector_code in vb["data"]["activity_sectors"].keys():
                                            activity_sector_percentage = vb["data"]["activity_sectors"][activity_sector_code]
                                            calculated_value = vb["data"]["value"]*activity_recipient_percentage*activity_sector_percentage if (activity_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                            converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                            recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                            to_di_id = activity_recipient_code
                                            sec_code = activity_sector_code
                                            pur_code = sec_code[:3] if sec_code is not None else None
                                            row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                            output.append(row)
                                else:
                                    #Just activity recipients
                                    for activity_recipient_code in vb["data"]["activity_recipients"].keys():
                                        activity_recipient_percentage = vb["data"]["activity_recipients"][activity_recipient_code]
                                        for transaction_sector_code in vb["data"]["transaction_sectors"].keys():
                                            transaction_sector_percentage = vb["data"]["transaction_sectors"][transaction_sector_code]
                                            calculated_value = vb["data"]["value"]*activity_recipient_percentage*transaction_sector_percentage if (activity_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                            converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                            recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                            to_di_id = activity_recipient_code
                                            sec_code = transaction_sector_code
                                            pur_code = sec_code[:3] if sec_code is not None else None
                                            row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                            output.append(row)
                            else:
                                if vb["data"]["use_activity_sectors"]:
                                    #Just activity sectors
                                    for transaction_recipient_code in vb["data"]["transaction_recipients"].keys():
                                        transaction_recipient_percentage = vb["data"]["transaction_recipients"][transaction_recipient_code]
                                        for activity_sector_code in vb["data"]["activity_sectors"].keys():
                                            activity_sector_percentage = vb["data"]["activity_sectors"][activity_sector_code]
                                            calculated_value = vb["data"]["value"]*transaction_recipient_percentage*activity_sector_percentage if (transaction_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                            converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                            recip = recode_if_not_none(transaction_recipient_code,self.dictionaries["recipient_dictionary"])
                                            to_di_id = transaction_recipient_code
                                            sec_code = activity_sector_code
                                            pur_code = sec_code[:3] if sec_code is not None else None
                                            row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                            output.append(row)
                                else:
                                    #Neither activity recipients nor sectors
                                    for transaction_recipient_code in vb["data"]["transaction_recipients"].keys():
                                        transaction_recipient_percentage = vb["data"]["transaction_recipients"][transaction_recipient_code]
                                        for transaction_sector_code in vb["data"]["transaction_sectors"].keys():
                                            transaction_sector_percentage = vb["data"]["transaction_sectors"][transaction_sector_code]
                                            calculated_value = vb["data"]["value"]*transaction_recipient_percentage*transaction_sector_percentage if (transaction_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                            converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                            recip = recode_if_not_none(transaction_recipient_code,self.dictionaries["recipient_dictionary"])
                                            to_di_id = transaction_recipient_code
                                            sec_code = transaction_sector_code
                                            pur_code = sec_code[:3] if sec_code is not None else None
                                            row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                            output.append(row)
                elif len(budget_output)==1:
                    #only one budget
                    vb = budget_output[0]
                    if vb["data"]["use_activity_recipients"]:
                        if vb["data"]["use_activity_sectors"]:
                            #Activity recipients and sectors
                            for activity_recipient_code in vb["data"]["activity_recipients"].keys():
                                activity_recipient_percentage = vb["data"]["activity_recipients"][activity_recipient_code]
                                for activity_sector_code in vb["data"]["activity_sectors"].keys():
                                    activity_sector_percentage = vb["data"]["activity_sectors"][activity_sector_code]
                                    calculated_value = vb["data"]["value"]*activity_recipient_percentage*activity_sector_percentage if (activity_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                    recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                    to_di_id = activity_recipient_code
                                    sec_code = activity_sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                    output.append(row)
                        else:
                            #Just activity recipients
                            for activity_recipient_code in vb["data"]["activity_recipients"].keys():
                                activity_recipient_percentage = vb["data"]["activity_recipients"][activity_recipient_code]
                                for transaction_sector_code in vb["data"]["transaction_sectors"].keys():
                                    transaction_sector_percentage = vb["data"]["transaction_sectors"][transaction_sector_code]
                                    calculated_value = vb["data"]["value"]*activity_recipient_percentage*transaction_sector_percentage if (activity_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                    recip = recode_if_not_none(activity_recipient_code,self.dictionaries["recipient_dictionary"])
                                    to_di_id = activity_recipient_code
                                    sec_code = transaction_sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                    output.append(row)
                    else:
                        if vb["data"]["use_activity_sectors"]:
                            #Just activity sectors
                            for transaction_recipient_code in vb["data"]["transaction_recipients"].keys():
                                transaction_recipient_percentage = vb["data"]["transaction_recipients"][transaction_recipient_code]
                                for activity_sector_code in vb["data"]["activity_sectors"].keys():
                                    activity_sector_percentage = vb["data"]["activity_sectors"][activity_sector_code]
                                    calculated_value = vb["data"]["value"]*transaction_recipient_percentage*activity_sector_percentage if (transaction_recipient_percentage is not None and activity_sector_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                    recip = recode_if_not_none(transaction_recipient_code,self.dictionaries["recipient_dictionary"])
                                    to_di_id = transaction_recipient_code
                                    sec_code = activity_sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                    output.append(row)
                        else:
                            #Neither activity recipients nor sectors
                            for transaction_recipient_code in vb["data"]["transaction_recipients"].keys():
                                transaction_recipient_percentage = vb["data"]["transaction_recipients"][transaction_recipient_code]
                                for transaction_sector_code in vb["data"]["transaction_sectors"].keys():
                                    transaction_sector_percentage = vb["data"]["transaction_sectors"][transaction_sector_code]
                                    calculated_value = vb["data"]["value"]*transaction_recipient_percentage*transaction_sector_percentage if (transaction_recipient_percentage is not None and transaction_sector_percentage is not None) else None
                                    converted_value = convert_usd(calculated_value,vb["data"]["year"],vb["data"]["currency"],self.dictionaries["ratedf"])
                                    recip = recode_if_not_none(transaction_recipient_code,self.dictionaries["recipient_dictionary"])
                                    to_di_id = transaction_recipient_code
                                    sec_code = transaction_sector_code
                                    pur_code = sec_code[:3] if sec_code is not None else None
                                    row = [vb["data"]["year"],recip,to_di_id,vb["data"]["flow_type_code"],vb["data"]["category"],vb["data"]["finance_type_code"],vb["data"]["aid_type_code"],converted_value,vb["data"]["short_description"],pur_code,sec_code,vb["data"]["channel_code"],vb["data"]["long_description"],vb["data"]["ftc"],vb["data"]["pba"],vb["data"]["b_or_t"],vb["data"]["budget_type"],vb["data"]["iati_identifier"],vb["data"]["incoming"]]
                                    output.append(row)
        return output