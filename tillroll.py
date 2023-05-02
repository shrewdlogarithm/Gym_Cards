import json
from datetime import datetime
from glob import glob

def addto(dct,ky,val):
    try:
        if ky in dct:
            dct[ky] += val
        else:
            dct[ky] = val
    except Exception as e:
        print(e)

dateformlong = '%Y-%m-%d %H:%M:%S' # javascript format

def gettilldata():
    ttypes = {"Total": 0}
    tilltrans = {}
    try:
        lfiles = glob("./logs/gympi-checkout*.log")
        for file in lfiles:
            with open(file) as lf:
                listo = lf.read()
                listo = listo.replace("\x00","")
                try: 
                    logs = json.loads("[" + listo[0:len(listo)-2] + "]")
                    for log in logs:
                        tdatefull = datetime.strptime(log["date"],dateformlong)
                        tdate = datetime.strftime(tdatefull,"%d/%m")
                        ttime = datetime.strftime(tdatefull,"%H:%M:%S")
                        if tdate not in tilltrans:
                            tilltrans[tdate] = {"times": {},"tots": {}}
                        if ttime not in tilltrans[tdate]["times"]:
                            tilltrans[tdate]["times"][ttime] = {"trans": [],"tots": {}}
                        for sale in log["sales"]:
                            if sale["type"] not in ttypes:
                                ttypes[sale["type"]] = 0
                            tilltrans[tdate]["times"][ttime]["trans"].append({"label": sale["label"],"type": sale["type"], "price": sale["price"]})
                            addto(tilltrans[tdate]["tots"],"Total",sale["price"])
                            addto(tilltrans[tdate]["tots"],sale["type"],sale["price"])
                            addto(tilltrans[tdate]["times"][ttime]["tots"],"Total",sale["price"])
                            addto(tilltrans[tdate]["times"][ttime]["tots"],sale["type"],sale["price"])
                        for tender in log["tender"]:
                            tilltrans[tdate]["times"][ttime]["trans"].append({"label": tender,"type": "Total", "price": log["tender"][tender]})
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)
    return {"tilltrans": tilltrans,"ttypes": ttypes}

# example = [
#     {"2023-04-27": [
#         {"00:58:32": [
#             {"drinks": 2.5}
#             {"protein": 35}
#             {"drinks": 2}
#         ]},
#     ]},
# ]

# {"sales": [{"type": "drinks", "price": 2.5}, {"type": "protein", "price": 35}, {"type": "drinks", "price": 2}], "tender": ["39.50", "3.00", "36.50"], "date": "2023-04-27 00:58:32"},
# {"sales": [{"type": "drinks", "price": 2.5}, {"type": "drinks", "price": 2}, {"type": "protein", "price": 35}], "tender": ["39.50"], "date": "2023-04-27 00:58:35"},
# {"sales": [{"type": "shortsubs", "price": 10}, {"type": "subs", "price": 25}], "tender": ["35.00"], "date": "2023-04-27 12:18:03"},
