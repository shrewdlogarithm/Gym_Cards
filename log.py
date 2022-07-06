import os,json,threading
import utils

lock = threading.Lock()
## Logs
logs = []
memdb = {}
def logname():
    return f'logs/gym-{utils.getnowlong().strftime("%Y%m%d")}.log'
def getmemdb():
    if not utils.getnowform() in memdb:
        memdb[utils.getnowform()] = {}
    return memdb[utils.getnowform()]
def memberin(memno):
    return memno in getmemdb()
def addlog(ev,card="",db={},excep=""):
    global logs
    lock.acquire()
    newlog = {
        "event": ev,       
        "dt": utils.getnowlong(),
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
    logs.append(newlog)
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(newlog,default=str) + ",\n")
    except Exception as e:
        print(f'Log Writing exception {e}')
    lock.release()
def membercount():
    return len(getmemdb())
def countmem(memno):
    if memberin(memno):
        del getmemdb()[memno]
    else:
        getmemdb()[memno] = True  
    return membercount()
def delmem(memno):
    if memberin(memno):
        del getmemdb()[memno]
try:
    if os.path.exists(logname()):
        with open(logname()) as lf:
            listo = lf.read()
            logs = json.loads("[" + listo[0:len(listo)-2] + "]")
except Exception as e:
    addlog("LoadingLogs",excep=e)
    logs = []
for log in logs:
    if log["event"] == "MemberInOut":
        countmem(log["db"]["memno"])
