import requests,time,threading,re,os,json
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

logfile = "logs/lockaccess.log"

def getlogs():
    logs = []
    try:
        if os.path.exists(logfile):
            with open(logfile) as lf:
                listo = lf.read()
                logs = json.loads("[" + listo[0:len(listo)-2] + "]")
    except Exception as e:
        pass 
    return logs

def getlockdb():
    logs = getlogs()
    lockdb = {}
    for log in logs:
        try:
            card = log[1].zfill(10)
        except Exception as e:
            print(e)
        if card in lockdb:
            lockdb[card].insert(0,log)
        else:
            lockdb[card] = [log]
    return lockdb

def writelog(rows):
    try:
        with open(logfile,"a+") as lf:
            for r in rows:
                lf.write(json.dumps(r,default=str) + ",\n")
    except Exception as e:
        pass

def readlogs(lasttime):
    # getpage("ACT_ID_1",{'s6': 'exit'}) # logout just because
    # time.sleep(1)
    # getpage("ACT_ID_1",{'username': 'abc',"pwd":"654321","logId":"20101222"}) # login because it might help?
    # time.sleep(1)
    rows = []
    un = 1
    done = False
    try:  
        page = getpage("ACT_ID_21",{'s4': 'Swipe'})
        while 1==1:
            # print("Reading Page",un)
            recid2 = 0
            pgs = re.findall(r"Page[^0-9]+?([0-9]+)[^0-9]+?Of[^0-9]+?([0-9]+)[^0-9]+?Page",page)
            pq = PyQuery(bytes(bytearray(page, encoding='utf-8')))
            for row in pq("table:last tr"):
                cells = []
                for cell in PyQuery(row)("td"):
                    cells.append(cell.text)
                if len(cells):
                    try:
                        if recid2 == 0:
                            recid2 = int(cells[0])-1
                    except Exception as e:
                        print("Failed with ", e)
                    # cells contains log rows
                    logdate = utils.parsedatelong(cells[4])
                    if lasttime == None or logdate > lasttime:
                        rows.append(cells)
                    else:
                        done = True
                        break;break
            if done or int(pgs[0][0]) >= int(pgs[0][1]):
                break
            else:
                page = getpage("ACT_ID_345",{
                    "PC":recid2,
                    "PE":"0",
                    "PN":"Next"})
                un += 1
    except Exception as e:
        print("Failed with ", e)
        # rows = [
        #     ["1","1","1","1",utils.getnowformlong()],
        #     ["1","2","1","1",utils.getnowformlong()],
        #     ["1","3","1","1",utils.getnowformlong()],
        #     ["1","5","1","1",utils.getnowformlong()],
        #     ["1","4","1","1",utils.getnowformlong()]
        # ]
    rows.sort(key=lambda x:x[4],reverse=False) # reverse the list
    return rows

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
    try:
        page = rs.post("http://" + lock_address + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': lock_address}, data = vars, timeout=3).text
        return page
    except Exception as e:
        print("Getpage failed with",e)
        return
    
def opendoor():
    try:
        client = RFIDClient(lock_address, controller_serial)
        client.open_door(1)
    except Exception as e:
        print("Open door failed >> ",e)
        return
