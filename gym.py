## LJ's Gym Membership System
##
## If you're reading this and you're not me, something bad has happened and I'm sorry you're stuck with sorting this out!
##
## This started as a Raspberry Pi project to add/remove/scan member cards - no screens at all - just beeps to tell if OK or expired
##
## It grew a bit...
## and... it's a bit of a spaghetti lashup in places to say the least - again, sorry!
##
## Start in the system folder - install.sh explains how to get it setup and the run/show.sh scripts fire-it-up
## Source is on github - link in the install script
##
## Weird Bits
##
## There is a sqlite database which stores all the log files for the DBStats page - which no-one really uses so don't worry about it too much
## 
## The system captures pictures via a webcam - this has NEVER been actually used and bits of it are commented out (showcards screen for example) 
##
## What we're using (specific requirements are in the install script - no requirements.txt because it varies depending on platform)
##
## Back-end is Python3
## Front-End served by FLASK using Jinja2 templates
## Front-end uses jQuery, TableSorter (card screen) and jQuery-TreeTable (tillroll) - all packaged locally
## Back-end talks to Front-End via SSE - can be moody (esp on Firefox) but works well enough if you use the right WSGI server
##
## This script can run standalone (python3 gym.py) for 1/2 clients (testing) OR via Gunicorn (using gevent as that supports SSE properly) for infinite clients (production)
##
## More comments appear in the code where I've remembered to make them - Good Luck!


import os,random,json,time,base64,shutil,subprocess,requests
from queue import Queue
from playsound import playsound
from flask import Flask, Response, request, render_template
import sse,log,threads,utils,lock,checkout
from datetime import timedelta
from threading import Timer

sysactive = True
nmemno = 0

dbname = "data/cards.json"
backdbname = dbname + ".bak"
carddb = {}

cards = Queue()
cardq=[]

log.addlog("GymStart")

## Database
def savedb():
    try:
        shutil.copy2(dbname,backdbname)
    except:
        pass # will fail on first run
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
    except Exception as e:
        log.addlog("LoadingBackDB",excep=e)
        carddb = {}
for c in carddb:
    if int(carddb[c]["memno"]) > nmemno:
        nmemno = int(carddb[c]["memno"])
savedb()
            

## Show images
def showpic(card):
    if (not log.memberin(card) and os.path.exists("site/images/" + str(carddb[card]["memno"]) + ".png")):
        sse.add_message("##MemImg" + str(carddb[card]["memno"]))

## Member Functions
def membername(card):
    memname = ""
    if (carddb[card]["name"] != ""):
        memname = carddb[card]["name"]
    elif utils.ismtype(carddb[card],"staff"):
        memname = "Staff-" + str(carddb[card]["memno"])
    else:
        memname = "Member-" + str(carddb[card]["memno"])
    if ("papermemno" in carddb[card] and carddb[card]["papermemno"] != ""):
        memname += " (" + carddb[card]["papermemno"] + ")"
    if utils.ismtype(carddb[card],"vip"):
        memname += " *FOB*"
    return memname

def membergreet(card):
    if card in carddb:
        if log.memberin(card):
            return ("Goodbye")
        else:
            return ("Welcome")
    else:
        return "Unknown Member"

def get_remain(card):
    if card in carddb:
        return (utils.parsedate(carddb[card]["expires"])-utils.getnow()).days
    else:
        return ""

def get_remainshow(card):
    return max(0,get_remain(card))

def getmemberstatus(card):
    gr = get_remain(card)
    if not utils.ismtype(carddb[card],"staff"):
        if (gr < 1):
            return ["expired",gr]
        elif (gr < 8):
            return ["renew",gr]
    return ["",0]
def memberstatus(card):
    ms = getmemberstatus(card)
    fn = "sounds/" + ms[0] + ".mp3"
    if os.path.exists(fn):
        try:
            playsound(fn)
        except:
            pass # doesn't work on Windows
    return ms

#Handle Cards
def addcard(card,mtype=0,name=""):
    global carddb,nmemno
    if (card not in carddb):
        nmemno += 1
        carddb[card] = {
            "created": utils.getnowform(),
            "lastseen": "",
            "expires": utils.getnowform(),
            "memno": nmemno,
            "papermemno": "",
            "name": name,
            "vip": mtype
        }
        carddb[card]["expires"] = utils.calc_expiry(carddb[card]["expires"])
        log.addlog("CardCreate",card,db=carddb[card])
        lock.updatelock(card,utils.ismtype(carddb[card],"vip"))
        savedb()
        return nmemno
    else:
        return -1 # this should never happen

def renewcard(card,mtype=0,name=""):
    carddb[card]["expires"] = utils.calc_expiry(carddb[card]["expires"])
    carddb[card]["name"] = name
    carddb[card]["vip"] = mtype
    log.addlog("CardRenew",card,db=carddb[card])
    lock.updatelock(card,utils.ismtype(carddb[card],"vip"))
    savedb()

def cardvisit(card):
    carddb[card]["lastseen"] = utils.getnowformlong()
    memname = carddb[card]["name"]
    if memname == "":
        memname = carddb[card]["memno"]
    log.countmem(card,memname,utils.getnowformlong())
    log.addlog("MemberInOut",card,db=carddb[card])
    sse.add_message(f'##Active Members {log.membercount()}')    
    savedb()
inputcard = ""
lastkey = utils.getnowlong()

## EvDev Input (USB RFID Reader) - this only works on *nix - not available for Windows
def eventinput():
    from select import select
    devs={}
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    devices = {dev.fd: dev for dev in devices}
    while sysactive:
        try:
            rffound = False
            for dev in devices:
                if "RFID" in devices[dev].name:
                    rffound = True
                    break;
            if not rffound:
                log.addlog("evdev_no_card_reader")
                raise Exception # reload devices
            r, w, x = select(devices,[],[],0.2)
            for fd in r:
                for event in devices[fd].read():  
                    if "RFID" in devices[fd].name:                          
                        if event.type == evdev.ecodes.EV_KEY:
                            try:
                                keyevent = evdev.categorize(event)
                                if (keyevent.keystate == keyevent.key_up):
                                    if (keyevent.keycode == "KEY_ENTER"):
                                        if (devs[fd] != ""):
                                            cards.put(devs[fd])
                                            devs[fd] = ""
                                    else:
                                        if (fd not in devs):
                                            devs[fd] = ""
                                        devs[fd] += keyevent.keycode.replace("KEY_","")                                
                            except Exception as e:
                                log.addlog("evdev_keyevent_exception",excep=e)
        except Exception as e: # this traps reloads AND devices which have disconnected
            sse.add_message("Card Reader not found")
            sse.add_message("##Timer" + str(3))
            threads.reset_timeout(3,kto)
            time.sleep(2)
            sse.add_message("")
            devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
            devices = {dev.fd: dev for dev in devices}

## Pynput- this has performance issues on *nix so I only use it for testing on Windows
def pyninput():
    while sysactive:
        try:                
            def on_press(key):
                global inputcard,lastkey
                if utils.getnowlong() - lastkey > timedelta(seconds=1):
                    inputcard = ""
                try:
                    if key == keyboard.Key.enter and inputcard != "":
                        cards.put(inputcard.zfill(10))
                        inputcard = ""
                    elif key.char in "0123456789":
                        inputcard += key.char
                        lastkey = utils.getnowlong()
                except Exception as e:
                    pass                

            # Collect events until released
            with keyboard.Listener(
                on_press=on_press) as listener:
                listener.join()

        except Exception as e:
            log.addlog("pynputexception",excep=e)

# if evdev isn't available we use pynput
try: 
    import evdev 
    threads.start_thread(eventinput)
except Exception as e:
    log.addlog("evdev_exception",excep=e)
    from pynput import keyboard
    # threads.start_thread(pyninput)

## Card Processing
def clearq():
    global cardq
    cardq = []

def addq(c):
    global cardq
    if c[0:2] == "@r":
        clearq()
        cardq.append({"cd": c[2:],"repl": True}) 
    elif c[0:2] == "@p":
        clearq()
        cardq.append({"cd": c[2:],"photo": True}) 
    else:
        cardq.append({"cd": c}) 

def getq():
    cseq = ""
    for q in cardq:
        if "repl" in q:
            nc = "Q"
        elif "photo" in q:
            nc = "P"
        elif q["cd"] in carddb:
            if utils.ismtype(carddb[q["cd"]],"staff"): 
                if cseq[0:1] == "M" and q["cd"] != cardq[0]["cd"]: # master cards other than the first seen aren't masters here
                    nc = "K"
                else:
                    nc = "M"
            else:
                nc = "K"
        else:
            nc = "U"
        cseq += nc
    return cseq  

## Handle card queue
def kto(tt=0):
    sse.add_message("Welcome!")
    if len(cardq):
        if getq() == "M": # deferred staff 'in out'
            card = cardq[0]["cd"]
            sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remainshow(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            cardvisit(card)
            sse.add_message("##Timer" + str(3))
            threads.reset_timeout(3,kto)
    clearq()

def handlecard(card):
    global sysactive
    if len(carddb) == 0:
        addcard(card,4)
        sse.add_message("Staff-1 Created")
    else:
        to = 0
        addq(card)
        cq=getq()
        if cq == "MMMMMM":
            sse.add_message("Shutdown")
            try:
                sysactive = False
                subprocess.call(['bash','system/backup.sh','shutdown'])
            except Exception as e:
                log.addlog("ShutdownFail",excep=e) 
            threads.stop_threads() 
            os._exit(4) # stops wsgi servers - sys.exit(4) does NOT work contrary to what the Internet says...
        elif cq == "MMMMM":
            sse.add_message("1 More to Shutdown")
            to = utils.getdelay(0)
        elif cq == "MMMM":
            sse.add_message("2 More to Shutdown")
            to = utils.getdelay(0)
        elif cq == "MMM": 
            sse.add_message("3 More to Shutdown")
            to = utils.getdelay(0)
        elif cq == "MMKM":
            card = cardq[2]["cd"]
            renewcard(card)
            sse.add_message(f'{membername(card)} <BR> { get_remainshow(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            clearq()
            to = utils.getdelay(1)
        elif cq[0:3] == "MMK" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()            
            to = utils.getdelay(0)
        elif cq == "MMK":
            sse.add_message("Swipe Staff to Renew <BR> Other to cancel")
            showpic(card)
            to = utils.getdelay(1)
        elif cq == "MMUM":
            mn = addcard(cardq[2]["cd"])
            sse.add_message("##MakeCap" + str(mn))
            sse.add_message(f'Member { mn } Created')
            clearq()
            to = utils.getdelay(1)
        elif cq[0:3] == "MMU" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
            to = utils.getdelay(0)
        elif cq == "MMU":
            sse.add_message("Swipe Staff to Add <BR> Other to cancel")
            sse.add_message("##ShowCap")
            to = utils.getdelay(2)
        elif cq[0] == "P" and len(cq) > 1:
            if cq == "PM":
                sse.add_message("##MakeCap" + str(carddb[cardq[0]["cd"]]["memno"]))
                sse.add_message("Photo Saved")
                to = utils.getdelay(1)
            else:
                sse.add_message("Cancelled")
                to = utils.getdelay(0)
            clearq()            
        elif cq == "P":
            sse.add_message("Swipe Staff to Take <BR> Other to cancel")
            sse.add_message("##ShowCap")            
            to = utils.getdelay(2)
        elif cq[0] == "Q" and len(cq) > 1:
            if cq == "QU":
                replcard = cardq[0]["cd"]
                card = cardq[1]["cd"]
                log.addlog("CardReplacedOld",replcard,db=carddb[replcard])
                lock.updatelock(replcard,False) 
                carddb[card] = carddb[replcard]
                if utils.ismtype(carddb[card],"vip"):
                    lock.updatelock(card,True) 
                if log.memberin(replcard): # card signed-in
                    cardvisit(replcard) # sign-out old card
                del carddb[replcard]
                log.addlog("CardReplacedNew",card,db=carddb[card])
                sse.add_message('Card Replaced')
                savedb()
            else:
                sse.add_message("Card already in use <BR> Replacement cancelled")
            clearq()
            to = utils.getdelay(1)
        elif cq == "Q":
            if cardq[0]["cd"] in carddb:
                sse.add_message(f'Swipe New Card for <BR> { membername(cardq[0]["cd"]) }')
            else:
                sse.add_message("Invalid Card - Cancelled") # this is driven from showcards so shouldn't happen
                clearq()
            to = utils.getdelay(1)
        elif cq == "MM":
            sse.add_message("Swipe Blank to Add <BR> Swipe Existing to Renew")
            to = utils.getdelay(1)
        elif cq == "MK": # special case - member arrives before staff sign-in expires
            card = cardq[1]["cd"]
            sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remainshow(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            cardvisit(card)
            clearq()
            to = utils.getdelay(1)
        elif cq == "MU" or cq == "U":
            sse.add_message("Unknown Card")
            clearq()
            to = utils.getdelay(1)
        elif len(cq) == 1:
            card = cardq[0]["cd"]
            if cq[0] == "K":
                sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remainshow(card) } days left:::{ memberstatus(card) }')
                showpic(card)
                cardvisit(card)
                clearq()
                to = utils.getdelay(1)
            else:
                sse.add_message(f'{ membername(card) }')
                to = utils.getdelay(0)
        else:
            sse.add_message("Welcome!")
            clearq()
        sse.add_message("##Timer" + str(to))
        threads.reset_timeout(to,kto)            

## Handle Inputs
def process_cards():
    while sysactive:
        time.sleep(.2) 
        while (not cards.empty()):
            handlecard(cards.get())
threads.start_thread(process_cards)

## Flask Server
app = Flask(__name__,
            static_url_path='', 
            static_folder='site')

@app.route('/theme.css')
def css():
    return render_template('theme.css',sett=utils.sett)

@app.route('/')
def root():
    if sysactive:
        return render_template('index.html',sett=utils.sett)
    else:
        return "System Shutting Down"

@app.route('/showstats')
def showstats():
    if sysactive:
        tvals = {
            "Members": "",
            "Total": len(carddb),
            "Current": 0,
            "Expired": 0,
            "Last 7 Days": "",
            "New": 0,
            "Visited": 0,
            "Next 7 Days": "",
            "Expiring": 0
        }
        rexp = []
        uexp = []
        for card in carddb:
            ms = getmemberstatus(card)
            if ms[0] == "renew":
                tvals["Expiring"] += 1
                if ms[1] < 4:
                    uexp.append(carddb[card]["name"])
            if ms[0] != "expired":
                tvals["Current"] += 1
            else:
                if ms[1] > -7:
                    rexp.append(carddb[card]["name"])
                tvals["Expired"] += 1
            fs = (utils.parsedate(carddb[card]["created"])-utils.getnow()).days
            if fs > -8:
                tvals["New"] += 1
            if carddb[card]["lastseen"] != "":
                try:
                    ls = (utils.parsedatelong(carddb[card]["lastseen"]).date()-utils.getnow()).days
                    if ls > -8:
                        tvals["Visited"] += 1
                except:
                    pass
        memsubs = {}
        def formatmem(lg):
            card = lg["card"]
            if card in carddb:
                rtn = carddb[card]["name"]
                if len(rtn) == 0:
                    rtn = "Unknown"
                if utils.ismtype(carddb[card],"vip"):
                    rtn += "*"
                rtn = str(carddb[card]["memno"]) + " - " + rtn
            else:
                if "db" in lg:
                    if "memno" in lg["db"]:
                        rtn = str(lg["db"]["memno"]) + " - *REMOVED*"
                    else:
                        rtn = "*REMOVED*"
            return rtn
        for x in range(0,15):
            ind = log.logdate(x).strftime("%a - (%d/%m)")
            memsubs[ind] = {}
            memsubs[ind][0] = []
            for lg in log.getlogmsgsfile("CardCreate",x):
                memsubs[ind][0].append(formatmem(lg))
            memsubs[ind][1] = []
            for lg in log.getlogmsgsfile("CardRenew",x):
                memsubs[ind][1].append(formatmem(lg))
        return render_template('showstats.html',tvals=tvals,rexp=sorted(rexp, key=str.casefold),uexp=sorted(uexp,key=str.casefold),memsubs=memsubs)
    else:
        return "System Shutting Down"

@app.route('/showstats1')
def showstats1():
    if sysactive:
        tvals = {
            " ": "All",
            "Members": len(carddb),
            "Current": 0,
            "Expired": 0,
            "  ": "Last 7 Days",
            "Visits": 0,
            "New": 0
        }
        rexp = {}
        uexp = {}
        visitdb= {}
        for card in carddb:
            ms = getmemberstatus(card)
            if ms[0] == "renew":
                if ms[1] < 14:
                    uexp[carddb[card]["memno"]] = ms[1]
                    visitdb[carddb[card]["memno"]] = {"name": carddb[card]["name"],"expires": ms[1],"visits": 0,"dayssincevisit": "30+"}
            if ms[0] != "expired":
                tvals["Current"] += 1
            else:
                if ms[1] > -7:
                    rexp[carddb[card]["memno"]] = ms[1]
                    visitdb[carddb[card]["memno"]] = {"name": carddb[card]["name"],"expires": ms[1],"visits": 0,"dayssincevisit": "30+"}
                tvals["Expired"] += 1
            fs = (utils.parsedate(carddb[card]["created"])-utils.getnow()).days
            if fs > -8:
                tvals["New"] += 1
            if carddb[card]["lastseen"] != "":
                try:
                    ls = (utils.parsedatelong(carddb[card]["lastseen"]).date()-utils.getnow()).days
                    if ls > -8:
                        tvals["Visits"] += 1
                except:
                    pass
                sql = "SELECT memno,SUM(1) AS visits,CAST(JULIANDAY('now')-JULIANDAY(MAX(dt)) as int) as dayssincevisit"
        for i in range(0,7):
            sql += ",SUM(IIF(STRFTIME('%w',dt)='" + str(i) + "',1,0)) AS DAY" + str(i)
        sql += " FROM LOGS WHERE dt > ? AND dt < ? AND event = 'MemberInOut' GROUP BY memno ORDER BY dayssincevisit "
        stime = (utils.getnow()+utils.relativedelta(months=-1)).strftime(utils.dateform)
        etime = utils.getnowform()
        mrows = log.connection.execute(sql,(stime,etime)).fetchall()
        for mr in mrows:
            if mr["memno"] in visitdb:
                visitdb[mr["memno"]] = visitdb[mr["memno"]] | dict(mr)
            tvals = tvals | {
                "Not Renewed": len(rexp),
                "   ": "Next 7 Days",
                "Expiring": len(uexp)
            }
        return render_template('showstats1.html',tvals=tvals,rexp=dict(sorted(rexp.items(),key=lambda x:x[1],reverse=True)),uexp=dict(sorted(uexp.items(),key=lambda x:x[1])),visitdb=visitdb,swipes=log.swdb)
    else:
        return "System Shutting Down"

@app.route('/checkout')
def checkouttemplate():
    if sysactive:
        return render_template('checkout.html',itemdb=checkout.itemdb,opt=utils.sett)
    else:
        return "System Shutting Down"

@app.route('/checkoutlog', methods=['POST'])
def checkoutlog():
    def getmtype(tx):
        if "vip" in tx:
            return tx["vip"]
        else:
            return 0        
    txdb  = request.get_json()
    checkout.addcheckoutlog(txdb)
    if "sales" in txdb:
        for tx in txdb["sales"]:
            if "type" in tx and tx["type"] == "Subscription" and "card" in tx and tx["card"] != "":
                tx["card"] = str(tx["card"]) # data attrs can be converted - we want a string
                if tx["card"] not in carddb:
                    addcard(tx["card"],getmtype(tx),tx["membername"])
                else:      
                    renewcard(tx["card"],getmtype(tx),tx["membername"])
    try:
        with open('/dev/ttyUSB0', 'w') as com:
            com.write(chr(27)+chr(112)+chr(0)+chr(48))
    except Exception as e:
        log.addlog("Cash Drawer Failure",excep=e)
    return("OK")

@app.route('/checkoutdata')
def sendtillroll():
    if sysactive:
         return render_template('checkoutdata.html',tilldata=checkout.getdata())
    else:
        return "System Shutting Down"

@app.route('/showcards')
def showcards():
    if sysactive:
        return render_template('showcards.html',carddb=carddb,memdb=log.getmemdb(),lockdb=lock.getlockdb(),mtypes=utils.mtypes)
    else:
        return "System Shutting Down"

@app.route('/settings')
def settings():
    if sysactive:
        return render_template('settings.html',sett=utils.sett)
    else:
        return "System Shutting Down"

@app.route('/update', methods=['POST'])
def update():
    global carddb
    if sysactive:
        card = request.form.get("card")
        if (card in carddb):
            try:
                log.addlog("UpdateBefore",card,db=carddb[card]) 
                if "name" in request.form:
                    carddb[card]["name"] = request.form.get("name")
                if "papermemno" in request.form:
                    carddb[card]["papermemno"] = request.form.get("papermemno")
                if "expires" in request.form:
                    carddb[card]["expires"] = utils.check_date(request.form.get("expires"),carddb[card]["expires"])
                if "vip" in request.form:
                    try: 
                        carddb[card]["vip"] = int(request.form.get("vip"))
                    except: 
                        carddb[card]["vip"] = 0
                lock.updatelock(card,utils.ismtype(carddb[card],"vip"))
                log.addlog("UpdateAfter",card,db=carddb[card])
                savedb()                
            except Exception as e:
                log.addlog("Update_exception",excep=e)
        return "Updated Successfully"
    else:
        return "System Shutting Down"

@app.route('/savesettings', methods=['POST'])
def savesettings():
    if sysactive:
        try:
            if "image" in request.files:
                file = request.files["image"]
                if file.filename:
                    adpic = "images/ad" +os.path.splitext(file.filename)[1]
                    utils.sett["adpic"] = adpic
                    file.save("site/" + adpic)
                    utils.savesett()
            if "delpic" in request.form and request.form["delpic"] == "on":
                try:
                    os.path.os.remove("site/" + utils.sett["adpic"])
                except:
                    pass
                if "adpic" in utils.sett:
                    del(utils.sett["adpic"])
                utils.savesett()
            log.addlog("Settings Before",0,db=utils.sett) 
            # Because HTML doesn't pass unchecked checkboxes...
            for st in [key for key in utils.sett if utils.sett[key] == "on"]:
                del utils.sett[st]
            for st in request.form:
                try:
                    utils.sett[st] = request.form[st]
                except:
                    pass
            log.addlog("Settings After",0,db=utils.sett)
            utils.savesett()
            sse.add_message("##Refresh")
        except Exception as e:
            log.addlog("Settings Exception",excep=e)
        return "Settings Updated Successfully"
    else:
        return "System Shutting Down"

@app.route('/takephoto', methods=['POST'])
def takephoto():
    if sysactive:
        card = request.form.get("card")
        if card in carddb:
            cards.put("@p" + card)
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/savepic', methods=['POST'])
def savepic():
    global carddb
    if sysactive:
        card = request.form.get("image")
        with open("site/images/" + request.form.get("memno") + ".png", "wb") as fh:
            imagedata = request.form.get("image")
            imagedata = imagedata.replace("data:image/png;base64,","")
            b64data = base64.b64decode(imagedata)
            fh.write(b64data)
        return "OK"
    else:
        return "System Shutting Down"

class DoorControl:
    dtimer = False
    logs = []
    lastdate = None
    checkneeded = False
    opendoor = False
    rs = None
    
    def __init__(self):
        self.dtimer = False
        logs = lock.getlogs()
        try:
            self.lastdate = utils.parsedatelong(logs[len(logs)-1][4])
        except:
            self.lastdate = utils.getnowlong()
        self.rs = requests.session()
        threads.start_thread(self.checker)
        threads.start_thread(self.dooropener)

    def dooropener(self):
        while sysactive:
            if self.opendoor:
                # using the relay directly to avoid multi-triggering the swipe
                try:
                    self.rs.get("http://shellyplus1-cc7b5c876d9c/relay/0?turn=off")
                except:
                    pass
                time.sleep(5)
                try:
                    self.rs.get("http://shellyplus1-cc7b5c876d9c/relay/0?turn=on")
                except:
                    pass
                self.opendoor = False
            else:
                time.sleep(5)
        #lock.opendoor()

    def cleartimer(self):
        if self.dtimer:
            self.dtimer.cancel()

    def starttimer(self):
        self.cleartimer()
        self.dtimer = Timer(10,self.alert)
        self.dtimer.start()

    def alert(self):
        # print("ALERT")
        self.starttimer()

    def checker(self):
        while 1==1:
            time.sleep(5)
            if self.checkneeded:
                self.docheck()

    def check(self):    
        self.checkneeded = True

    def docheck(self):        
        try:
            logs=lock.readlogs(self.lastdate)            
            try:
                if (len(logs)):
                    cardsread = {}
                    for log in logs:
                        self.lastdate = utils.parsedatelong(log[4])
                        card = log[1].zfill(10)
                        if card in carddb:
                            since = 99
                            if card in cardsread:
                                since = self.lastdate - cardsread[card]
                            if since > 5: # ignore multi-swipes inside 5s
                                cardsread[card] = utils.parsedatelong(log[4])
                                clearq()
                                handlecard(card)
                                time.sleep(2)
                    lock.writelog(logs)
                    self.checkneeded = False
            except Exception as e:
                # we didn't get anything from the lock
                pass

        except Exception as e:
            return(str(e))
        
doorc = DoorControl()

@app.route('/swipe', methods=['POST'])
def swipe():
    if sysactive:
        clearq()
        card = request.form.get("card")
        if card in carddb:
            handlecard(card)
            if request.form.get("door"):
                doorc.opendoor = True
            return "OK"
        else:
            return "Not Found"
    else:
        return "System Shutting Down"

# called by the relay when the door 'opens'
@app.route('/dooropen')
def dooropen():
    if sysactive:
        doorc.starttimer()   
        doorc.check()     
        return "OK"
    else:
        return "System Shutting Down"

# called by the door magnet when it closes
@app.route('/doorclose')
def doorclose():
    if sysactive:
        doorc.cleartimer()
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/checkcard', methods=['POST'])
def checkcard():
    card = request.form.get("card")
    if card in carddb:
        return carddb[card] | {"staff": utils.mtypes[carddb[card]["vip"]]["staff"],"newexpires": utils.calc_expiry(carddb[card]["expires"])}
    else:
        return "Not Found",404

    
@app.route('/replace', methods=['POST'])
def replace():
    if sysactive:
        cards.put("@r"+request.form.get("card")) 
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/delphoto', methods=['POST'])
def delphoto():
    if sysactive:
        card = request.form.get("card")
        if card in carddb:
            try:
                os.remove("site/images/" + str(carddb[card]["memno"]) + ".png")
                log.addlog("DelPhoto",card)
            except Exception as e:
                log.addlog("DelPhoto",excep=e)
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/delmember', methods=['POST'])
def delmember():
    if sysactive:
        card = request.form.get("card")
        if card in carddb:
            lock.updatelock(card,False)
            log.delmem(card)
            log.addlog("DelMember",card,db=carddb[card])
            del carddb[card]
            savedb()
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/stream')
def stream():
    sse.add_message("##Timeset" + utils.getnowformlong()) # this ensures every stream gets a time update 
    def stream():
        messages = sse.announcer.listen()  
        sse.add_message(f'##Active Members {log.membercount()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

@app.context_processor
def handle_context():
    return dict(os=os,random=random)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)