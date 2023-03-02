from datetime import timedelta

import os,json,threading,socket
import utils

lock = threading.Lock()
memdb = {}

def logdate(dys=0):
    offs = timedelta(days=dys)
    return utils.getnow() - offs

def logname(dys=0):    
    return f'logs/{socket.gethostname()}-{logdate(dys).strftime("%Y%m%d")}.log'

def addlog(ev,card="",db={},excep=""):
    lock.acquire()
    newlog = {
        "event": ev,       
        "dt": utils.getnowformlong(),
        "card": card,
        "db": db,
        "excep": excep
    }
    if (card != ""):
        newlog["card"] = card
    if (db != ""):
        newlog["db"] = db
    if (excep != ""):
        newlog["excep"] = excep
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(newlog,default=str) + ",\n")
    except Exception as e:
        print(f'Log Writing exception {e}')
    lock.release()

def getmemdb():
    global memdb
    if not utils.getnowform() in memdb:
        memdb[utils.getnowform()] = {}
    return memdb[utils.getnowform()]

def memberin(memno):
    return memno in getmemdb()

def countmem(memno):
    if memberin(memno):
        del getmemdb()[memno]
    else:
        getmemdb()[memno] = True  

def membercount():
    return len(getmemdb())


def delmem(memno):
    if memberin(memno):
        del getmemdb()[memno]

def getlogmsgs(typ,dys=0):
    logs = []
    retlogs = []
    try:
        if os.path.exists(logname(dys)):
            with open(logname(dys)) as lf:
                listo = lf.read()
                logs = json.loads("[" + listo[0:len(listo)-2] + "]")
    except Exception as e:
        addlog("GetLogMsgs",excep=e)
        logs = []
    for log in logs:
        if log["event"] == typ:
            retlogs.append(log)
    return retlogs
            
logs = getlogmsgs("MemberInOut")
for log in logs:
    countmem(log["db"]["memno"])