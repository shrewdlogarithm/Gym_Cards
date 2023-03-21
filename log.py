from datetime import timedelta

import os,json,threading,socket
import utils

import sqlite3
dbname = "./data/logs.sqlite"
connection = sqlite3.connect(dbname, check_same_thread=False)
connection.row_factory = sqlite3.Row

lock = threading.Lock()
memdb = {}

def logdate(dys=0):
    offs = timedelta(days=dys)
    return utils.getnow() - offs

def logdtfrom(dys=0):
    return logdate(dys+1).strftime("%Y-%m-%d 23:59:59")

def logdtto(dys=0):
    return logdate(dys-1).strftime("%Y-%m-%d 00:00:00")

def logname(dys=0):    
    #return f'logs/{socket.gethostname()}-{logdate(dys).strftime("%Y%m%d")}.log'
    return f'logs/gympi-{logdate(dys).strftime("%Y%m%d")}.log'

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
    memno = None
    if (db != ""):
        newlog["db"] = db
        if "memno" in db:
            memno = db["memno"]
    if (excep != ""):
        newlog["excep"] = excep
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(newlog,default=str) + ",\n")
    except Exception as e:
        print(f'Log Writing exception {e}')    
    connection.execute("INSERT INTO LOGS (dt,memno,event,card,db,excep) VALUES(?,?,?,?,?,?)",(newlog["dt"],memno,newlog["event"],newlog["card"],json.dumps(newlog["db"]),str(newlog["excep"])))
    connection.commit()
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

def getlogmsgs(type,dys=0):
    print(logdtfrom(dys),logdtto(dys))
    mrows = connection.execute("SELECT * FROM LOGS WHERE dt > ? AND dt < ? AND event = ?",(logdtfrom(dys),logdtto(dys),type)).fetchall()
    return mrows
    
def getlogmsgsfile(typ,dys=0):    
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
    countmem(log["memno"])