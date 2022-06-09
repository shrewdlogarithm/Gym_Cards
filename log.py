import json
from datetime import datetime
## Logs
logs = []
def logname():
    return f'logs/gym-{datetime.now().strftime("%Y%m%d")}.log'
def addlog(ev,card="",db="",excep=""):
    global logs
    newlog = {
        "dt": datetime.now(),
        "offdt": datetime.now(),
        "event": ev,
        
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
try:
    if os.path.exists(logname()):
        with open(logname()) as lf:
            listo = lf.read()
            logs = json.loads("[" + listo[0:len(listo)-2] + "]")
except Exception as e:
    addlog("LoadingLogs",excep=e)
    logs = []

for log in logs:
    if ("card" in log):
        handlemember(log["card"])
