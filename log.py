import os,json
from datetime import datetime
## Logs
logs = []
def logname():
    return f'logs/gym-{datetime.now().strftime("%Y%m%d")}.log'
def addlog(ev,card="",db={},excep=""):
    global logs
    newlog = {
        "event": ev,       
        "dt": datetime.now(),
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
memdb = {}
def membercount():
    return len(memdb)
def countcard(card):
    if card in memdb:
        del memdb[card]
    else:
        memdb[card] = True  
    return membercount()
def memberin(card):
    return card in memdb

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
        countcard(log["card"])
