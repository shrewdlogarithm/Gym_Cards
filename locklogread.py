import lock
import utils

logs = lock.getlogs()
lastdate = utils.parsedatelong(logs[len(logs)-1][4])
rows=lock.readlogs(lastdate)
lock.writelog(rows)

print("Lock Read Completed Successfully")