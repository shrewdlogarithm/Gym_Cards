import os,json,time,base64,shutil
from random import randrange
from datetime import timedelta
from queue import Queue
from playsound import playsound
from flask import Flask, Response, request, render_template
import sse,log,threads,utils # our own libraries

sysactive = True

## Database
dbname = "data/cards.json"
backdbname = dbname + ".bak"
carddb = {}
def savedb():
    try:
        shutil.copy2(dbname,backdbname)
    except:
        pass # doesn't exist first run
    with open(dbname, 'w') as json_file:
        json.dump(carddb, json_file, indent=4,default=str)        

try:
    if os.path.exists(dbname):
        with open(dbname) as json_file:
            carddb = json.load(json_file)
except Exception as e:
    log.addlog("LoadingDB",excep=e)
    try: 
        if os.path.exists(backdbname):
            with open(backdbname) as json_file:
                carddb = json.load(json_file)
        log.addlog("LoadingDB",excep=e)
    except Exception as e:
        log.addlog("LoadingBackDB",excep=e)
        carddb = {}
nmemno = 0
for c in carddb:
    if (int(carddb[c]["memno"]) > nmemno):
        nmemno = int(carddb[c]["memno"])

#Handle Cards
def addcard(card,staff=False):
    global carddb
    if (card not in carddb):
        memno = 0
        for c in carddb:
            if (int(carddb[c]["memno"]) > memno):
                memno = int(carddb[c]["memno"])
        memno += 1
        carddb[card] = {
            "staff": staff,
            "created": utils.getnowform(),
            "lastseen": "",
            "expires": utils.getrenewform(),
            "memno": memno,
            "papermemno": "",
            "name": ""
        }
        log.addlog("CardCreate",card,db=carddb[card])
        savedb()
        return memno
    else:
        return -1 # this should really never happen...

from datetime import datetime,timedelta

testdays = 900
today = datetime.now().date()
adddate = datetime.now().date() - timedelta(days=testdays)
while adddate < today:
    cn = randrange(100000,999999)
    addcard(cn)
    carddb[cn]["name"] = "Hello"
    savedb()
    adddate += timedelta(days=1)
    print(adddate)