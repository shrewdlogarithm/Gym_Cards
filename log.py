from datetime import timedelta

import os,json,threading,socket
import utils

import sqlite3
dbname = "./db/logs.sqlite"
connection = sqlite3.connect(dbname, check_same_thread=False)
connection.row_factory = sqlite3.Row
connection.execute("CREATE TABLE IF NOT EXISTS LOGS (dt TEXT NOT NULL,memno INTEGER, event TEXT NOT NULL, card TEXT NOT NULL, db TEXT, excep TEXT);")
connection.execute("CREATE INDEX IF NOT EXISTS LOGS_event_dt ON LOGS (event,dt);")
connection.execute("CREATE INDEX IF NOT EXISTS LOGS_dt ON LOGS (dt) ;")
connection.execute("CREATE INDEX IF NOT EXISTS LOGS_memno ON LOGS (memno);")


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

def memberin(card):
    return card in getmemdb()

swdb = []
def countmem(card,name,dt):
    if memberin(card):
        swdb[getmemdb()[card]]["maxdt"] = dt
        del getmemdb()[card]
    else:
        swdb.append({
            "card": card,
            "name": name,
            "mindt": dt,
            "maxdt": ""
        })
        getmemdb()[card] = len(swdb)-1

def membercount():
    return len(getmemdb())


def delmem(card):
    if memberin(card):
        del getmemdb()[card]

def getlogmsgs(type,dys=0):
    print(logdtfrom(dys),logdtto(dys))
    mrows = connection.execute("SELECT * FROM LOGS WHERE dt > ? AND dt < ? AND event = ?",(logdtfrom(dys),logdtto(dys),type)).fetchall()
    mret = []
    for m in mrows:
        mr = dict(m)
        if "db" in mr:
            mr["db"] = json.loads(mr["db"])
        mret.append(mr)
    return mret
    
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

def loadlogs():
    def getname(log):
        if "db" in log:
            if "name" in log["db"] and log["db"]["name"] != "":
                return log["db"]["name"]
            elif "memno" in log["db"]:
                return log["db"]["memno"]
            else:
                return "unknown"
        else:
            return "unknown"
    logs = getlogmsgs("MemberInOut")
    for log in logs:    
        countmem(log["card"],getname(log),log["dt"])
loadlogs()