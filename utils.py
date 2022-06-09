from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta # needed for 'month' addition

dateform = '%Y-%m-%d' # the format Chrome requires...
def formdate(dt):
    return dt.strftime(dateform)

def getnow():
    return datetime.now().date()

def getnowform(of=timedelta(days=0)):
    return formdate(getnow()+of)

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
