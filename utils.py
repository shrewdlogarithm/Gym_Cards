from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta # needed for 'month' addition

dateform = '%Y-%m-%d' # the format Chrome requires...
dateformlong = '%Y-%m-%d-%H:%M:%S' # the format Chrome requires...
def formdate(dt):
    return dt.strftime(dateform)

def formdatelong(dt):
    return dt.strftime(dateformlong)

def getnow():
    return datetime.now().date()

def getnowlong():
    return datetime.now()

def getnowform(of=timedelta(days=0)):
    return formdate(getnow()+of)

def getnowformlong(of=timedelta(days=0)):
    return formdatelong(getnowlong()+of)

def getdate(dtstr):
    return datetime.strptime(dtstr,dateform).date()

def getrenew(dt=datetime.now()):
    return dt+relativedelta(months=1)

def getrenewform(dt=datetime.now()):
    return formdate(getrenew(dt))

def check_date(newdate,fbdate):
    try:
        ndate = formdate(getdate(newdate))
        return ndate
    except:
        return fbdate
