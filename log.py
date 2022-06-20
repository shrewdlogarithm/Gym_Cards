import os,json
import utils
from datetime import datetime
## Logs
logs = []
memdb = {}
def logname():
    return f'logs/gym-{utils.getnowform()}.log'
def getmemdb():
    if utils.getnowform() in memdb:
        return memdb[utils.getnowform()]
    else:
        return {}
def memberin(memno):
    return memno in getmemdb()
def addlog(ev,card="",db={},excep=""):
    global logs,memdb
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
def membercount():
    return len(getmemdb())
def countmem(memno):
    if memberin(memno):
        del memdb[utils.getnowform()][memno]
    else:
        if not utils.getnowform() in memdb:
            memdb[utils.getnowform()] = {}
        memdb[utils.getnowform()][memno] = True  
    return membercount()
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
