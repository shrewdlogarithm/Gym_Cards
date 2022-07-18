import time,threading,json,os,requests
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta 
from pyquery import PyQuery
import sse,log

try:
    from rfid import RFIDClient
except: 
    pass

timeoffset = timedelta()
dateform = '%Y-%m-%d' # the format Chrome requires..
dateformlongfbms = '%Y-%m-%d %H:%M:%S.%f' # original format
dateformlongfb = '%Y-%m-%d-%H:%M:%S' # older format
dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format
lock_address = "192.168.1.143"
controller_serial = 123209978

##Settings
stname = "data/settings.json"
sett = {
    "theme0": "#000000","theme1": "#ffffff","theme2": "#333333","theme3": "#acf310",
    "ad1": "","ad2": "", "adpic": "",
    "ad1col": "#ffffff","ad2col": "#ffffff","ad3col": "#ffffff",
    "dshort": "2","dmedium": "5","dlong": "0"
}
def savesett():
    with open(stname, 'w') as json_file:
        json.dump(sett, json_file, indent=4,default=str)        

if os.path.exists(stname):
    with open(stname) as json_file:
        sett = {**sett,**json.load(json_file)}
else:
    savesett()

def getdelay(dl): 
    delays = ["short","medium","long"]
    try:
        rv = int(sett["d"+delays[dl]])
    except:
        rv = 0
    return rv

def formdatelong(dt):
    return dt.strftime(dateformlong)

def formdate(dt):
    return dt.strftime(dateform)

def getnowlong():    
    return datetime.now()+timeoffset

def getnow():
    return getnowlong().date()

def getnowformlong():
    return formdatelong(getnowlong())

def getnowform():
    return formdate(getnow())

def getdate(dtstr):
    return datetime.strptime(dtstr,dateform).date()

def getdatelong(dtstr):
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

def getrenew(dt=0):
    if dt == 0:
        dt = getnowlong()
    return dt+relativedelta(months=1)

def getrenewform(dt=0):
    if dt == 0:
        dt = getnowlong()
    return formdate(getrenew(dt))

def check_date(newdate,fbdate):
    try:
        ndate = formdate(getdate(newdate))
        return ndate
    except:
        return fbdate

def calc_expiry(expdate):
    expdate = getdate(expdate)
    if expdate-getnow() >= timedelta(days=-7):
        return getrenewform(expdate)
    else:
        return getrenewform()

def setnow(dt):
    global timeoffset
    timeoffset = dt - datetime.now()
    sse.add_message("##Timeset" + getnowformlong())

def addlock(card):
    try:
        client = RFIDClient(lock_address, controller_serial)
        client.add_user(int(card), [1]) 
    except Exception as e:
        raise e

def remlock(card):
    try:
        client = RFIDClient(lock_address, controller_serial)
        client.remove_user(int(card))
    except Exception as e:
        raise e

def background(f):
    def backgrnd_func(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return backgrnd_func

@background
def handlelock(card,add):
    try:
        if add:
            log.addlog("LockAdd",card) 
            addlock(card)
        else:
            log.addlog("LockRemove",card)
            remlock(card)
    except Exception as e:
        log.addlog("LockExcept",excep=e)

def getpage(path,vars={}):
    global lockavail
    try:
        page = requests.post("http://" + lock_address + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': "192.168.1.143"}, data = vars, timeout=3).text
        return page
    except Exception as e:
        raise e

@background
def getlocktime():
    maxtries = 5
    timefound = False
    while not timefound:
        try:
            page = getpage("ACT_ID_21",{"s5": "Configure"})
            pq = PyQuery(bytes(bytearray(page, encoding='utf-8')))
            d = pq("table:last tr:nth-of-type(5) td:nth-of-type(2)")
            dd = getdatelong(d[0].text)
            dn = getnowlong()
            if dn < dd: 
                setnow(dd)
                log.addlog("Datetime: Using Lock time " + getnowformlong())        
            else:
                log.addlog("Datetime: Using System time " + getnowformlong())
            timefound = True
        except Exception as e:
            log.addlog("DatetimeExcept",excep=e)
            if maxtries > 1:
                maxtries -= 1
                time.sleep(10)
            else:                
                break
getlocktime()
