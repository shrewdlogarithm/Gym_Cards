from datetime import timedelta,datetime

import json,threading
import utils,log

from glob import glob
dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format

thrlock = threading.Lock()

itemdb = {
    "0": {
        "Membership": {
            "color": "limegreen",
            "items": [
                {"title": "1-Day Member","price": 4.5},
                {"title": "1-Week Member","price": 15},
                ],
            },
        "Subscription": {
            "color": "yellow",
            "items": [                
                ],
            },
        "Drinks": {
            "color": "blue",
            "items": [
                {"title": "Water","price": .7},
                {"title": "Energy Drink","price": 1},
                {"title": "Energy Drink","price": 1.65},
                {"title": "Energy Drink","price": 2},
                {"title": "Energy Drink","price": 2.50},
            ],
        },
        "Protein": {
            "color": "lightblue",
            "items": [
                {"title": "Protein Tub","price": 47},
            ],
        },
    },
    "1": {
        "Notes": {
            "color": "green",
            "items": [
                {"title": "Note","price": 20},
                {"title": "Note","price": 10},
                {"title": "Note","price": 5},
            ],
        },
        "Coins": {
            "color": "grey",
            "items": [
                {"title": "Coin","price": 2},
                {"title": "Coin","price": 1},
            ],
        },
        "Exact": {
            "color": "blue",
            "items": [
                {"title": "Card","price": -1},
                {"title": "Bank","price": -1},
                {"title": "Cash","price": -1},
            ]
        },
    },
    "2": {
        "row1": {
            "color": "orange",
            "items": [
                {"title": "1","price": 0},
                {"title": "2","price": 0},
                {"title": "3","price": 0},
            ],
        },
        "row2": {
            "color": "orange",
            "items": [
                {"title": "4","price": 0},
                {"title": "5","price": 0},
                {"title": "6","price": 0},
            ],
        },
        "row3": {
            "color": "orange",
            "items": [
                {"title": "7","price": 0},
                {"title": "8","price": 0},
                {"title": "9","price": 0},
            ],
        },
        "row4": {
            "color": "orange",
            "items": [
                {"title": "0","price": 0},
                {"title": "00","price": 0},
                {"title": "<<<","price": 0},
            ],
        },
    }
}
for mtype in utils.mtypes:
    if not utils.mtypes[mtype]["staff"]:
        itemdb["0"]["Subscription"]["items"].append(
            {"title": "Subs " + utils.mtypes[mtype]["name"], "price": utils.mtypes[mtype]["price"], "vip": mtype}
        )

def logdate(dys=0):
    offs = timedelta(days=dys)
    return utils.getnow() - offs

def logname(dys=0):    
    return f'logs/{utils.sett["systemname"]}-{logdate(dys).strftime("%Y%m%d")}.checkout'

def addcheckoutlog(db):
    thrlock.acquire()
    db["date"] = utils.getnowformlong()
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(db,default=str) + ",\n")
    except Exception as e:
        log.addlog("AddCheckOutLog",excep=e)    
    thrlock.release()

def addto(dct,ky,val):
    try:
        if ky in dct:
            dct[ky] = f'{round(float(dct[ky]) + val,2):.2f}'
        else:
            dct[ky] = f'{round(val,2):.2f}'
    except Exception as e:
        log.addlog("AddTo",excep=e)    

def getdata():
    ttypes = {"Total": 0}
    tilltrans = {}
    try:
        lfiles = glob(f"./logs/{utils.sett['systemname']}*.checkout")
        for file in lfiles:
            with open(file) as lf:
                listo = lf.read()
                listo = listo.replace("\x00","")
                try: 
                    logs = json.loads("[" + listo[0:len(listo)-2] + "]")
                    for logline in logs:
                        tdatefull = datetime.strptime(logline["date"],dateformlong)
                        tdate = datetime.strftime(tdatefull,"%y/%m/%d")
                        ttime = datetime.strftime(tdatefull,"%H:%M:%S")
                        if tdate not in tilltrans:
                            tilltrans[tdate] = {"times": {},"tots": {},"age": (tdatefull-datetime.today()).days}
                        if ttime not in tilltrans[tdate]["times"]:
                            tilltrans[tdate]["times"][ttime] = {"trans": [],"tots": {}}
                        for sale in logline["sales"]:
                            if sale["type"] not in ttypes:
                                ttypes[sale["type"]] = 0
                            tilltrans[tdate]["times"][ttime]["trans"].append(sale)
                            addto(tilltrans[tdate]["tots"],"Total",sale["price"])
                            addto(tilltrans[tdate]["tots"],sale["type"],sale["price"])
                            addto(tilltrans[tdate]["times"][ttime]["tots"],"Total",sale["price"])
                            addto(tilltrans[tdate]["times"][ttime]["tots"],sale["type"],sale["price"])
                        for tender in ["Total","Change","Paid","Staff"]:
                            if tender in logline["tender"]:
                                if tender == "Paid" or tender == "Staff":
                                    tilltrans[tdate]["times"][ttime]["trans"].append({"label": tender + ":" + logline["tender"][tender],"type": "Total"})
                                else:
                                    tilltrans[tdate]["times"][ttime]["trans"].append({"label": tender,"type": "Total", "price": logline["tender"][tender]})
                except Exception as e:
                    log.addlog("GetDataLoop",excep=e)    
    except Exception as e:
        log.addlog("GetData",excep=e)    
    return {"tilltrans": tilltrans,"ttypes": ttypes}
