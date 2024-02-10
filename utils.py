import json,os,socket
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta 

dateform = '%Y-%m-%d' # the format Chrome requires..
dateformlongfbms = '%Y-%m-%d %H:%M:%S.%f' # original format
dateformlongfb = '%Y-%m-%d-%H:%M:%S' # older format
dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format

##Settings
stname = "data/settings.json"
sett = {
    "theme0": "#000000","theme1": "#ffffff","theme2": "#333333","theme3": "#acf310",
    "ad1": "","ad2": "", "adpic": "",
    "ad1col": "#ffffff","ad2col": "#ffffff","ad3col": "#ffffff",
    "dshort": "2","dmedium": "5","dlong": "0",
    "adcount": 8, "adtime": 2000,
    "systemname": f"{socket.gethostname()}"
}
def savesett():
    with open(stname, 'w') as json_file:
        json.dump(sett, json_file, indent=4,default=str)        

if os.path.exists(stname):
    with open(stname) as json_file:
        sett = {**sett,**json.load(json_file)}

savesett()

def getdelay(dl): 
    delays = ["short","medium","long"]
    try:
        rv = int(sett["d"+delays[dl]])
    except:
        rv = 0
    return rv

def getnowlong():    
    return datetime.now()

def getnow():
    return getnowlong().date()

def getnowformlong():
    return getnowlong().strftime(dateformlong)

def getnowform():
    return getnow().strftime(dateform)

def parsedate(dtstr):
    return datetime.strptime(dtstr,dateform).date()

def parsedatelong(dtstr):
    try:
        return datetime.strptime(dtstr,dateformlong)
    except:
        try:
            return datetime.strptime(dtstr,dateformlongfb)
        except Exception as e:
            try:
                return datetime.strptime(dtstr,dateformlongfbms)
            except:
                pass

def check_date(newdate,fbdate):
    try:
        ndate = parsedate(newdate).strftime(dateform)
        return ndate
    except:
        return fbdate

def getrenewform(dt=0):
    if dt == 0:
        dt = getnowlong()
    return (dt+relativedelta(months=1)).strftime(dateform)

def calc_expiry(expdate):
    expdate = parsedate(expdate)
    if expdate-getnow() >= timedelta(days=-7):
        return getrenewform(expdate)
    else:
        return getrenewform()
    
mtypes = {
    1: {"name": "Lite", "price": 20, "vip": False, "staff": False},
    0: {"name": "Normal", "price": 25, "vip": False, "staff": False},
    5: {"name": "Junior VIP", "price": 25, "vip": True, "staff": False},
    2: {"name": "VIP", "price": 30, "vip": True, "staff": False},
    3: {"name": "Couple", "price": 40, "vip": False, "staff": False},
    4: {"name": "Staff", "price": 0, "vip": False, "staff": True},
}
def ismtype(cdb,typ):
    return "vip" in cdb and cdb["vip"] in mtypes and mtypes[cdb["vip"]][typ]
