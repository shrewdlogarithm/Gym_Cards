import lock
import utils

lastdate = None

logs = lock.getlogs()
if len(logs):
    lastdate = utils.parsedatelong(logs[len(logs)-1][4])

try:
    rows=lock.readlogs(lastdate)
    lock.writelog(rows)
except Exception as e:
    print(e)

print("Lock Read Ended")