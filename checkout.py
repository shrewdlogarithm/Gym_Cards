from datetime import timedelta

import json,threading
import utils

lock = threading.Lock()

# import sqlite3
# dbname = "./data/logs.sqlite"
# connection = sqlite3.connect(dbname, check_same_thread=False)
# connection.row_factory = sqlite3.Row
# connection.execute("CREATE TABLE IF NOT EXISTS LOGS (dt TEXT NOT NULL,memno INTEGER, event TEXT NOT NULL, card TEXT NOT NULL, db TEXT, excep TEXT);")
# connection.execute("CREATE INDEX IF NOT EXISTS LOGS_event_dt ON LOGS (event,dt);")
# connection.execute("CREATE INDEX IF NOT EXISTS LOGS_dt ON LOGS (dt) ;")
# connection.execute("CREATE INDEX IF NOT EXISTS LOGS_memno ON LOGS (memno);")

itemdb = {
    "sales": {
        "subs": {
            "color": "pink",
            "items": [
                {"title": "Subs","price": 30},
                {"title": "Subs","price": 40},
                ],
            },
        "drinks": {
            "color": "blue",
            "items": [
                {"title": "Water","price": .75},
                {"title": "Energy Drink","price": 1},
                {"title": "Energy Drink","price": 2},
                {"title": "Energy Drink","price": 2.50},
            ],
        },
        "protein": {
            "color": "yellow",
            "items": [
                {"title": "Protein Scoop","price": 2},
                {"title": "Protein Tub","price": 25},
                {"title": "Protein Tub","price": 35},
            ],
        },
        "other": {
            "color": "red",
            "items": [
                {"title": "Random Item","price": 12.65},
                {"title": "Random Thingy","price": 77.12},
            ],
        },
    },
    "tender": {
        "cash": {
            "color": "green",
            "items": [
                {"title": "Note","price": 50},
                {"title": "Note","price": 20},
                {"title": "Note","price": 10},
                {"title": "Note","price": 5},
            ],
        },
        "funnymoney": {
            "color": "yellow",
            "items": [
                {"title": "LeeBucks","price": 5},
                {"title": "LeeBucks","price": 2},
                {"title": "LeeBucks","price": 1},
            ],
        },
        "other": {
            "color": "blue",
            "items": [
                {"title": "Card","price": -1},
                {"title": "Bank","price": -1}
            ]
        },
    }
}

def logdate(dys=0):
    offs = timedelta(days=dys)
    return utils.getnow() - offs

def logname(dys=0):    
    return f'logs/gympi-checkout-{logdate(dys).strftime("%Y%m%d")}.log'

def addcheckoutlog(db):
    lock.acquire()
    db["date"] = utils.getnowformlong()
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(db,default=str) + ",\n")
    except Exception as e:
        print(f'Log Writing exception {e}')    
    # connection.execute("INSERT INTO LOGS (dt,memno,event,card,db,excep) VALUES(?,?,?,?,?,?)",(newlog["dt"],memno,newlog["event"],newlog["card"],json.dumps(newlog["db"]),str(newlog["excep"])))
    # connection.commit()
    lock.release()