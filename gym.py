import os,json,time,base64,shutil,subprocess
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
    global carddb,nmemno
    if (card not in carddb):
        nmemno += 1
        carddb[card] = {
            "staff": staff,
            "created": utils.getnowform(),
            "lastseen": "",
            "expires": utils.getrenewform(),
            "memno": nmemno,
            "papermemno": "",
            "name": ""
        }
        log.addlog("CardCreate",card,db=carddb[card])
        savedb()
        return nmemno
    else:
        return -1 # this should really never happen...
def calc_expiry(card):
    expdate = utils.getdate(carddb[card]["expires"])
    if expdate-utils.getnow() >= timedelta(days=-7):
        return utils.getrenewform(expdate)
    else:
        return utils.getrenewform()
def cardvisit(card):
    carddb[card]["lastseen"] = utils.getnowform()
    log.addlog("MemberInOut",card,db=carddb[card])
    sse.add_message(f'##Active Members {log.countcard(card)}')    
    savedb()
def renewcard(card):
    carddb[card]["expires"] = calc_expiry(card)
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
        return "StaffMember" + str(carddb[card]["memno"])
    else:
        return "Member" + str(carddb[card]["memno"])
def membergreet(card):
    if card in carddb and not carddb[card]["staff"]:
        if log.memberin(card):
            return ("Goodbye")
        else:
            return ("Welcome")
    else:
        return ""
def memberstatus(card):
    gr = get_remain(card)
    if (gr < 1):
        try:
            playsound('sounds/expired.mp3')
        except:
            pass
        return "expired"
    elif (gr < 8):
        try:
            playsound('sounds/renew.mp3')
        except:
            pass
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
                cards.put(input())
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
    #if len(qq) > 0 and utils.getnow()-qq[0]["dt"] > timedelta(seconds=5):
    #    clearq()        
    if c[0:2] == "@r":
        qq.append({"cd": c[2:],"repl": True,"dt": utils.getnow()}) 
    else:
        qq.append({"cd": c,"dt": utils.getnow()}) 
def getq():
    cseq = ""
    for q in qq:
        if "repl" in q:
            nc = "Q"
        elif q["cd"] in carddb:
            if carddb[q["cd"]]["staff"]: # is a master card
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

def kto(tt=0):
    if len(qq):
        if  tt > 2:
            sse.add_message("Welcome!")
        elif getq()[0] == "M": # deferred staff 'in out'
            cardvisit(qq[0]["cd"])
    clearq()
def handlecard(card):
    global sysactive
    if len(carddb) == 0:
        addcard(card,True)
        sse.add_message("Staff Card Created")
    else:
        to = 0
        addq(card)
        cq=getq()
        if cq == "MMMMMM":
            sse.add_message("Shutdown")
            try:
                sysactive = False
                threads.stop_threads()
                try:
                    subprocess.call(['bash','system/backup.sh','shutdown'])
                except:
                    pass
            except:
                pass
        elif cq == "MMMMM":
            sse.add_message("Swipe ONE more time to Shutdown")
            to = 2
        elif cq == "MMMM":
            sse.add_message("Swipe TWO more times to Shutdown")
            to = 2
        elif cq == "MMM": # special case for shutdown only - we want to NOT clear but put screen back to normal??
            sse.add_message("Swipe THREE more times to Shutdown")
            to = 2
        elif cq == "MMKM":
            card = qq[2]["cd"]
            renewcard(card)
            sse.add_message(f'Member { membername(card) } <BR> { get_remain(card) } days left')
            clearq()
        elif cq[0:3] == "MMK" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
        elif cq == "MMK":
            sse.add_message("Swipe Staff Card to Renew <BR> Any other to cancel")
            to = 5
        elif cq == "MMUM":
            mn = addcard(qq[2]["cd"])
            sse.add_message(f'Member { mn } Created')
            clearq()
        elif cq[0:3] == "MMU" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
        elif cq == "MMU":
            sse.add_message("Swipe Staff Card to Add <BR> Any other to cancel")
            to = 10
        elif cq == "MMQ":
            if qq[2]["cd"] in carddb:
                sse.add_message(f'Swipe card to replace for { membername(qq[2]["cd"]) }')
                to = 10
            else:
                sse.add_message("Invalid Card - cannot replace")
                clearq()
        elif cq[0:3] == "MMQ" and len(cq) > 3:
            if cq == "MMQU":
                replacecard(qq[2]["cd"],qq[3]["cd"])
            else:
                sse.add_message("Card already in use <BR> Replacement cancelled")
            clearq()
        elif cq == "MM":
            sse.add_message("Add or Renew a Card")
            to = 5
        elif cq == "MK":
            card = qq[1]["cd"]
            sse.add_message(f'{membergreet(card) } { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
            cardvisit(card)
            clearq()
        elif cq == "MU" or cq == "U":
            sse.add_message("Unknown Card")
            clearq()
        elif len(cq) == 1:
            card = qq[0]["cd"]
            sse.add_message(f'{membergreet(card) } { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
            if cq[0] == "K":
                cardvisit(card)
                clearq()
            else:
                to = 2
        else:
            sse.add_message("Welcome!")
            clearq()

        if to:
            threads.reset_timeout(to,kto)


def process_cards():
    while sysactive:
        time.sleep(.2) # this avoids thrashing 1 core constantly...
        while (not cards.empty()):
            handlecard(cards.get())
threads.start_thread(process_cards)

## Flask Server
app = Flask(__name__,
            static_url_path='', 
            static_folder='site')

@app.route('/')
def root():
    if sysactive:
        return render_template('index.html')
    else:
        return "System Shutting Down"

@app.route('/showcards')
def showcards():
    if sysactive:
        return render_template('showcards.html',carddb=carddb)
    else:
        return "System Shutting Down"

@app.route('/webcam')
def webcam():
    if sysactive:
        return render_template('webcam.html')
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
                try: 
                    carddb[card]["staff"] = request.form.get("staff").lower()=="on"
                except:
                    carddb[card]["staff"] = False
                log.addlog("UpdateAfter",card,db=carddb[card])
                savedb()
            except Exception as e:
                log.addlog("Update_exception",excep=e)
        return "Updated Successfully"
    else:
        return "System Shutting Down"

@app.route('/savepic', methods=['POST'])
def savepic():
    global carddb
    if sysactive:
        card = request.form.get("image")
        with open("images/imageToSave.png", "wb") as fh:
            imagedata = request.form.get("image")
            imagedata = imagedata.replace("data:image/png;base64,","")
            b64data = base64.b64decode(imagedata)
            fh.write(b64data)
    return("OK")

@app.route('/replace', methods=['POST'])
def replace():
    global replcard, mode
    if sysactive:
        clearq()
        stm = 0
        for card in carddb:
            if carddb[card]["staff"]:
                stm = card
                break
        if stm:
            handlecard(stm) # TODO if member 1 is NOT staff, this won't work!>
            handlecard(stm)
            handlecard("@r"+request.form.get("card")) # TODO r might not be enough - maybe @@ or something like that?
        else:
            print("ERROR: Cannot find staff member")
        return "OK"
    else:
        return "System Shutting Down"

@app.route('/stream')
def stream():
    def stream():
        messages = sse.announcer.listen()  
        sse.add_message(f'##Active Members {log.membercount()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)