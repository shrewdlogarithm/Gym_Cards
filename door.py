import utils,log,threads,time

ip_address = "192.168.1.143"
controller_serial = 123209978
try:
    from rfid import RFIDClient
except: 
    pass

def addlock(card):
    try:
        client = RFIDClient(ip_address, controller_serial)
        client.add_user(int(card), [1]) 
    except Exception as e:
        raise e

def remlock(card):
    try:
        client = RFIDClient(ip_address, controller_serial)
        client.remove_user(int(card))
    except Exception as e:
        raise e

from datetime import datetime
from pyquery import PyQuery
import requests

def getpage(path,vars={}):
    global lockavail
    try:
        page = requests.post("http://" + ip_address + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': "192.168.1.143"}, data = vars, timeout=3).text
        return page
    except Exception as e:
        raise e

def getlocktime():
    timefound = False
    while not timefound:
        try:
            page = getpage("ACT_ID_21",{"s5": "Configure"})
            pq = PyQuery(bytes(bytearray(page, encoding='utf-8')))
            d = pq("table:last tr:nth-of-type(5) td:nth-of-type(2)")
            dd = utils.getdatelong(d[0].text)
            dn = utils.getnowlong()
            if dn < dd: 
                log.addlog("Datetime: Using Lock time " + utils.formdatelong(dd))        
                utils.setnow(dd)
            else:
                log.addlog("Datetime: Using local time " + utils.formdatelong(dn))
            timefound = True
        except:
            time.sleep(5)
threads.start_thread(getlocktime)