client = False
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
import re,json
import requests

lockavail = True
def getpage(file,path,vars={}):
    global lockavail
    if lockavail:
        try:
            return requests.post(lock + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': "192.168.1.143"}, data = vars).text
        except:
            lockavail = False
    if not lockavail:
        #return datetime.now()
        return("<table><tr></tr><tr></tr><tr></tr><tr></tr><tr><td></td><td>2022-07-07 20:05:00</td></tr></table>")

def getlocktime():
    page = getpage("act5.html","ACT_ID_21",{"s5": "Configure"})
    pq = PyQuery(bytes(bytearray(page, encoding='utf-8')))

    # find door time and check it's offset
    d = pq("table:last tr:nth-of-type(5) td:nth-of-type(2)")
    dd = datetime.strptime(d[0].text,'%Y-%m-%d %H:%M:%S')
    dn = datetime.now()
    if dn < dd:    
        print("Lock time is ahead by " + str(dd-dn))

getlocktime()