import requests,time,threading
from pyquery import PyQuery
import log,utils

try:
    from rfid import RFIDClient
except: 
    pass

#lock_address = "127.0.0.1"
lock_address = "192.168.1.143"
controller_serial = 123209978

def background(f):
    def bg_f(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return bg_f

@background
def updatelock(card,add):
    try:
        if add:
            log.addlog("LockAdd",card) 
            client = RFIDClient(lock_address, controller_serial)
            client.add_user(int(card), [1]) 
        else:
            log.addlog("LockRemove",card)
            client = RFIDClient(lock_address, controller_serial)
            client.remove_user(int(card))
    except Exception as e:
        log.addlog("LockExcept",excep=e)

rs = requests.session()

def getpage(path,vars={}):
    global lockavail
    try:
        page = rs.post("http://" + lock_address + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': lock_address}, data = vars, timeout=3).text
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
            dd = utils.parsedatelong(d[0].text)
            dn = utils.getnowlong()
            if dn < dd: 
                utils.setnow(dd)
                log.addlog("Datetime: Using Lock time " + utils.getnowformlong())        
            else:
                log.addlog("Datetime: Using System time " + utils.getnowformlong())
            timefound = True
        except Exception as e:
            log.addlog("DatetimeExcept",excep=e)
            if maxtries > 1:
                maxtries -= 1
                time.sleep(10)
            else:                
                break
getlocktime()