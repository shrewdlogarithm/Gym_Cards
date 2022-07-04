import os,json,time,base64,shutil,subprocess
from queue import Queue
from playsound import playsound
from flask import Flask, Response, request, render_template
import sse,log,threads,utils,door

log.addlog("GymStart")

sysactive = True

##Settings
stname = "data/settings.json"
sett = {
    "theme0": "#000000","theme1": "#ffffff","theme2": "#333333","theme3": "#acf310",
    "ad1": "","ad2": "", "adpic": "",
    "ad1col": "#ffffff","ad2col": "#ffffff","ad3col": "#ffffff",
    "dshort": "2","dmedium": "5","dlong": "0"
}
def savesett():
    with open(stname, 'w') as json_file:
        json.dump(sett, json_file, indent=4,default=str)        

if os.path.exists(stname):
    with open(stname) as json_file:
        sett = {**sett,**json.load(json_file)}
else:
    savesett()
def getdelay(dl): # TODO use this
    try:
        rv = int(sett["d"+dl])
    except:
        rv = 0
    return rv

## Database
dbname = "data/cards.json"
backdbname = dbname + ".bak"
carddb = {}
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
    global carddb,nmemno
    if (card not in carddb):
        nmemno += 1
        carddb[card] = {
            "staff": staff,
            "created": utils.getnowform(),
            "lastseen": "",
            "expires": utils.getnowform(),
            "memno": nmemno,
            "papermemno": "",
            "name": "",
            "vip": False
        }
        carddb[card]["expires"] = utils.calc_expiry(carddb[card]["expires"])
        log.addlog("CardCreate",card,db=carddb[card])
        savedb()
        return nmemno
    else:
        return -1 # this should never happen
def cardvisit(card):
    carddb[card]["lastseen"] = utils.getnowformlong()
    log.addlog("MemberInOut",card,db=carddb[card])
    sse.add_message(f'##Active Members {log.countmem(carddb[card]["memno"])}')    
    savedb()
def renewcard(card):
    carddb[card]["expires"] = utils.calc_expiry(carddb[card]["expires"])
    log.addlog("CardRenew",card,db=carddb[card])
    savedb()
def get_remain(card):
    if card in carddb:
        return max(0,(utils.getdate(carddb[card]["expires"])-utils.getnow()).days+1,0)
    else:
        return ""
def replacecard(replcard,card):
    log.addlog("CardReplacedOld",replcard,db=carddb[replcard])
    carddb[card] = carddb[replcard]
    if log.memberin(carddb[replcard]["memno"]): # how are they in but have no card - who knows? :)
        log.countmem(carddb[replcard]["memno"])
    if log.memberin(carddb[replcard]["memno"]): # card signed-in
        cardvisit(replcard) # sign-out old card
    del carddb[replcard]
    log.addlog("CardReplacedNew",card,db=carddb[card])
    sse.add_message('Card Replaced')
    savedb()

## Member Functions
def membername(card):
    if (carddb[card]["name"] != ""):
        return carddb[card]["name"]
    elif (carddb[card]["papermemno"] != ""):
        return carddb[card]["papermemno"]
    elif (carddb[card]["staff"]):
        return "Staff-" + str(carddb[card]["memno"])
    else:
        return "Member-" + str(carddb[card]["memno"])
def membergreet(card):
    if card in carddb:
        if log.memberin(carddb[card]["memno"]):
            return ("Goodbye")
        else:
            return ("Welcome")
    else:
        return "Unknown Member"
def memberstatus(card):
    gr = get_remain(card)
    if (gr < 1):
        try:
            playsound('sounds/expired.mp3')
        except:
            pass # doesn't work on Windows
        return "expired"
    elif (gr < 8):
        try:
            playsound('sounds/renew.mp3')
        except:
            pass # doesn't work on Windows
        return "renew"
    else:
        return ""

## Read Cards
cards = Queue()

## EvDev Input (USB RFID Reader)
def eventinput():
    try: 
        import evdev
        from select import select
        devs={}
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        devices = {dev.fd: dev for dev in devices}
        while sysactive:
            try:
                r, w, x = select(devices,[],[],0.2)
                for fd in r:
                    for event in devices[fd].read():                            
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
            except Exception as e:
                    log.addlog("evdev_device_exception",excep=e)
    except: # evdev n/a on Windows so we use Input() instead
        while sysactive:
            try:
                ip = input()
                cards.put(ip)
            except Exception as e:
                log.addlog("KeyInput_exception",excep=e)
threads.start_thread(eventinput)

## Process Cards
qq=[]
def clearq():
    global qq
    qq = []
def addq(c):
    global qq
    if c[0:2] == "@r":
        clearq()
        qq.append({"cd": c[2:],"repl": True}) 
    elif c[0:2] == "@p":
        clearq()
        qq.append({"cd": c[2:],"photo": True}) 
    elif c[0:2] == "@m":
        mn = c[2:]
        for card in carddb:
            if carddb[card]["memno"] == int(mn):
                qq.append({"cd": card})
                break
    else:
        qq.append({"cd": c}) 
def getq():
    cseq = ""
    for q in qq:
        if "repl" in q:
            nc = "Q"
        elif "photo" in q:
            nc = "P"
        elif q["cd"] in carddb:
            if carddb[q["cd"]]["staff"]: 
                if cseq[0:1] == "M" and q["cd"] != qq[0]["cd"]: # master cards other than the first seen aren't masters here
                    nc = "K"
                else:
                    nc = "M"
            else:
                nc = "K"
        else:
            nc = "U"
        cseq += nc
    return cseq  

def showpic(card):
    if (not log.memberin(carddb[card]["memno"]) and os.path.exists("site/images/" + str(carddb[card]["memno"]) + ".png")):
        sse.add_message("##MemImg" + str(carddb[card]["memno"]))
def kto(tt=0):
    sse.add_message("Welcome!")
    if len(qq):
        if getq() == "M": # deferred staff 'in out'
            card = qq[0]["cd"]
            sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            cardvisit(card)
            sse.add_message("##Timer" + str(3))
            threads.reset_timeout(3,kto)

    clearq()
def handlecard(card):
    global sysactive
    if len(carddb) == 0:
        addcard(card,True)
        sse.add_message("Staff-1 Created")
    else:
        to = 0
        addq(card)
        cq=getq()
        if cq == "MMMMMM":
            sse.add_message("Shutdown")
            try:
                sysactive = False
                threads.stop_threads()
                subprocess.call(['bash','system/backup.sh','shutdown'])
            except Exception as e:
                log.addlog("ShutdownFail",excep=e) 
        elif cq == "MMMMM":
            sse.add_message("1 More to Shutdown")
            to = 2
        elif cq == "MMMM":
            sse.add_message("2 More to Shutdown")
            to = 2
        elif cq == "MMM": 
            sse.add_message("3 More to Shutdown")
            to = 2
        elif cq == "MMKM":
            card = qq[2]["cd"]
            renewcard(card)
            sse.add_message(f'{membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            clearq()
            to = 5
        elif cq[0:3] == "MMK" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()            
            to = 2
        elif cq == "MMK":
            sse.add_message("Swipe Staff to Renew <BR> Other to cancel")
            showpic(card)
            to = 5
        elif cq == "MMUM":
            mn = addcard(qq[2]["cd"])
            sse.add_message("##MakeCap" + str(mn))
            sse.add_message(f'Member { mn } Created')
            clearq()
            to = 5
        elif cq[0:3] == "MMU" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
            to = 2
        elif cq == "MMU":
            sse.add_message("Swipe Staff to Add <BR> Other to cancel")
            sse.add_message("##ShowCap")
            to = 0
        elif cq[0] == "P" and len(cq) > 1:
            if cq == "PM":
                sse.add_message("##MakeCap" + str(carddb[qq[0]["cd"]]["memno"]))
                sse.add_message("Photo Saved")
                to = 5
            else:
                sse.add_message("Cancelled")
                to = 2
            clearq()            
        elif cq == "P":
            sse.add_message("Swipe Staff to Take <BR> Other to cancel")
            sse.add_message("##ShowCap")            
            to = 0
        elif cq[0] == "Q" and len(cq) > 1:
            if cq == "QU":
                replacecard(qq[0]["cd"],qq[1]["cd"])
            else:
                sse.add_message("Card already in use <BR> Replacement cancelled")
            clearq()
            to = 5
        elif cq == "Q":
            if qq[0]["cd"] in carddb:
                sse.add_message(f'Swipe New Card for <BR> { membername(qq[0]["cd"]) }')
            else:
                sse.add_message("Invalid Card - Cancelled") # this is driven from showcards so shouldn't happen
                clearq()
            to = 10
        elif cq == "MM":
            sse.add_message("Swipe Blank to Add <BR> Swipe Existing to Renew")
            to = 5
        elif cq == "MK": # special case - member arrives before staff sign-in expires
            card = qq[1]["cd"]
            sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
            showpic(card)
            cardvisit(card)
            clearq()
            to = 5
        elif cq == "MU" or cq == "U":
            sse.add_message("Unknown Card")
            clearq()
            to = 5
        elif len(cq) == 1:
            card = qq[0]["cd"]
            if cq[0] == "K":
                sse.add_message(f'{membergreet(card) } <BR> { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
                showpic(card)
                cardvisit(card)
                clearq()
                to = 5
            else:
                sse.add_message(f'{ membername(card) }')
                to = 2
        else:
            sse.add_message("Welcome!")
            clearq()

        sse.add_message("##Timer" + str(to))
        threads.reset_timeout(to,kto)            

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
    return render_template('theme.css',sett=sett)

@app.route('/')
def root():
    if sysactive:
        return render_template('index.html',sett=sett)
    else:
        return "System Shutting Down"

@app.route('/showcards')
def showcards():
    if sysactive:
        return render_template('showcards.html',carddb=carddb,memdb=log.getmemdb())
    else:
        return "System Shutting Down"

@app.route('/settings')
def settings():
    if sysactive:
        return render_template('settings.html',sett=sett)
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
                carddb[card]["name"] = request.form.get("name")
                carddb[card]["papermemno"] = request.form.get("papermemno")
                carddb[card]["expires"] = utils.check_date(request.form.get("expires"),carddb[card]["expires"])
                if carddb[card]["memno"] != 1:
                    try: 
                        carddb[card]["staff"] = request.form.get("staff").lower()=="yes"
                    except:
                        carddb[card]["staff"] = False
                try: 
                    carddb[card]["vip"] = request.form.get("vip").lower()=="yes"
                except:
                    carddb[card]["vip"] = False
                log.addlog("UpdateAfter",card,db=carddb[card])
                savedb()                
                
                try:
                    if carddb[card]["vip"]:
                        log.addlog("LockAdd",card)
                        door.addlock(card)
                    else:
                        log.addlog("LockRemove",card)
                        door.remlock(card)
                except Exception as e:
                    log.addlog("LockExcept",excep=e)

            except Exception as e:
                log.addlog("Update_exception",excep=e)
        return "Updated Successfully"
    else:
        return "System Shutting Down"

@app.route('/savesettings', methods=['POST'])
def savesettings():
    global sett
    if sysactive:
        try:
            if "image" in request.files:
                file = request.files["image"]
                if file.filename:
                    adpic = "images/ad" +os.path.splitext(file.filename)[1]
                    sett["adpic"] = adpic
                    file.save("site/" + adpic)
                    savesett()
            if "delpic" in request.form and request.form["delpic"] == "on":
                try:
                    os.path.os.remove("site/" + sett["adpic"])
                except:
                    pass
                if "adpic" in sett:
                    del(sett["adpic"])
                savesett()
            log.addlog("Settings Before",0,db=sett) 
            for st in sett:
                try:
                    sett[st] = request.form[st]
                except:
                    pass
            log.addlog("Settings After",0,db=sett)
            savesett()
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
            clearq()
            handlecard("@p" + card)
        return "OK"
    else:
        return "System Shutting Down"
    return("OK")

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
    return("OK")

@app.route('/swipe', methods=['POST'])
def swipe():
    if sysactive:
        clearq()
        card = request.form.get("card")
        if card in carddb:
            handlecard(card)
            return "OK"
        else:
            return "Not Found"
    else:
        return "System Shutting Down"

@app.route('/replace', methods=['POST'])
def replace():
    global replcard, mode
    if sysactive:
        clearq()
        handlecard("@r"+request.form.get("card")) 
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/delphoto', methods=['POST'])
def delphoto():
    global replcard, mode
    if sysactive:
        card = request.form.get("card")
        if card in carddb:
            try:
                os.remove("site/images/" + str(carddb[card]["memno"]) + ".png")
            except Exception as e:
                log.addlog("DelPhoto",excep=e)
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/delmember', methods=['POST'])
def delmem():
    global replcard, mode
    if sysactive:
        card = request.form.get("card")
        if card in carddb:
            log.delmem(carddb[card]["memno"])
            del carddb[card]
            savedb()
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/stream')
def stream():
    sse.add_message("##Timeset" + utils.getnowformlong())
    def stream():
        messages = sse.announcer.listen()  
        sse.add_message(f'##Active Members {log.membercount()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

@app.context_processor
def handle_context():
    return dict(os=os)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)