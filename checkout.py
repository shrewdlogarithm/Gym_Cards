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
    "0": {
        "membership": {
            "color": "limegreen",
            "items": [
                {"title": "1-Day Member","price": 3.5},
                {"title": "1-Week Member","price": 10},
                ],
            },
        "subs": {
            "color": "yellow",
            "items": [
                {"title": "Monthly Lite","price": 20},
                {"title": "Monthly","price": 25},
                {"title": "Monthly VIP","price": 30},
                ],
            },
        "drinks": {
            "color": "blue",
            "items": [
                {"title": "Water","price": .7},
                {"title": "Energy Drink","price": 1},
                {"title": "Energy Drink","price": 1.5},
                {"title": "Energy Drink","price": 2},
            ],
        },
        "protein": {
            "color": "lightblue",
            "items": [
                {"title": "Protein Tub","price": 35},
            ],
        },
    },
    "1": {
        "cash": {
            "color": "green",
            "items": [
                {"title": "Note","price": 50},
                {"title": "Note","price": 20},
                {"title": "Note","price": 10},
                {"title": "Note","price": 5},
            ],
        },
        "other": {
            "color": "blue",
            "items": [
                {"title": "Card","price": -1},
                {"title": "Bank","price": -1},
                {"title": "Exact Cash","price": -1},
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
                {"title": "<<","price": 0},
            ],
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