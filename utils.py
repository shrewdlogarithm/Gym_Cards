from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta # needed for 'month' addition

dateform = '%Y-%m-%d' # the format Chrome requires...
dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format
def formdate(dt):
    return dt.strftime(dateform)

def formdatelong(dt):
    return dt.strftime(dateformlong)

def getnowlong():
    return datetime.now()

def getnow():
    return getnowlong().date()

def getnowform():
    return formdate(getnow())

def getnowformlong():
    return formdatelong(getnowlong())

def getdate(dtstr):
    return datetime.strptime(dtstr,dateform).date()

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
