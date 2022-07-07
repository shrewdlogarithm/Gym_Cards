from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta # needed for 'month' addition
import sse

dateform = '%Y-%m-%d' # the format Chrome requires..
dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format

def formdatelong(dt):
    return dt.strftime(dateformlong)

def formdate(dt):
    return dt.strftime(dateform)

def getnowlong():    
    return localtime

def getnow():
    return getnowlong().date()

def getnowformlong():
    return formdatelong(getnowlong())

def getnowform():
    return formdate(getnow())

def getdate(dtstr):
    return datetime.strptime(dtstr,dateform).date()

def getdatelong(dtstr):
    return datetime.strptime(dtstr,dateformlong)

def getrenew(dt=0):
    if dt == 0:
        dt = getnowlong()
    return dt+relativedelta(months=1)

def getrenewform(dt=0):
    if dt == 0:
        dt = getnowlong()
    return formdate(getrenew(dt))

def check_date(newdate,fbdate):
    try:
        ndate = formdate(getdate(newdate))
        return ndate
    except:
        return fbdate

def calc_expiry(expdate):
    expdate = getdate(expdate)
    if expdate-getnow() >= timedelta(days=-7):
        return getrenewform(expdate)
    else:
        return getrenewform()

localtime = 0
def setnow(dt):
    global localtime
    localtime = dt
    sse.add_message("##Timeset" + getnowformlong())
setnow(datetime.now())
