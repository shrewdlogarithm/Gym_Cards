import time,lock,json,os,requests
import utils

rs = requests.session()

logfile = "locklogread.json"

lastdate = None
logs = []
try:
    if os.path.exists(logfile):
        with open(logfile) as lf:
            listo = lf.read()
            logs = json.loads("[" + listo[0:len(listo)-2] + "]")
        lastdate = utils.parsedatelong(logs[len(logs)-1][4])
except Exception as e:
    pass 

lock.getpage("ACT_ID_1",{'s6': 'exit'}) # logout just because
time.sleep(1)
lock.getpage("ACT_ID_1",{'username': 'abc',"pwd":"654321","logId":"20101222"}) # login because it might help?
time.sleep(1)
lastdate,rows=lock.readlogs(lastdate)
rows.sort(key=lambda x:x[4],reverse=False)
try:
    with open(logfile,"a") as lf:
        for r in rows:
            lf.write(json.dumps(r,default=str) + ",\n")
except Exception as e:
    pass
print("Done")