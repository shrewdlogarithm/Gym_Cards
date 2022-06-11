import os,json,time,base64,shutil
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
    shutil.copy2(dbname,backdbname)
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
        log.addlog("CardCreate",card)
        savedb()
        return memno
    else:
        return -1 # this should really never happen...
def calc_expiry(card):
    expdate = utils.getdate(carddb[card]["expires"])
    if expdate-utils.getnow() >= timedelta(days=-7):
        return utils.getrenewform(expdate)
    else:
        return utils.getrenewform()
def cardvisit(card):
    log.addlog("MemberInOut",card)
    sse.add_message(f'{membergreet(card) } { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
    carddb[card]["lastseen"] = utils.getnowform()
    savedb()
    sse.add_message(f'##Active Members {log.countmember(card)}')
def renewcard(card):
    carddb[card]["expires"] = calc_expiry(card)
    log.addlog("CardRenew",card)
    savedb()
def get_remain(card):
    if card in carddb:
        return max(0,(utils.getdate(carddb[card]["expires"])-utils.getnow()).days+1,0)
    else:
        return ""
replcard=""
def replacecard(card):
    global replcard
    log.addlog("CardReplacedOld",replcard)
    carddb[card] = carddb[replcard]
    sse.sse.add_message(f'##Replaced Card OK!')
    log.addlog("CardReplacedNew",card)
    del carddb[replcard]
    replcard = ""
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
    if card in carddb:
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
                r, w, x = select(devices,[],[])
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
    except Exception as e: # evdev n/a on Windows so we use Input() instead
        while sysactive:
            try:
                cards.put(input())
            except Exception as e:
                log.addlog("KeyInput_exception",excep=e)
threads.start_thread(eventinput)

## Process Cards
mode = 0
lastcard = {"card": -1}
adhits = 0
def handle_card(card):
    global mode,lastcard,adhits
    if (lastcard["card"] in carddb and utils.getnow()-lastcard["dt"] < timedelta(seconds=5) and card in carddb and carddb[lastcard["card"]]["staff"] and carddb[card]["staff"]):
        adhits += 1
    else:
        adhits = 0
    lastcard = {"card": card,"dt": utils.getnow()}
    if (len(carddb) == 0):
        addcard(card,True)
        sse.add_message("Master Card Created")
    elif (mode == 0):
        if (card in carddb):
            if (carddb[card]["staff"]):
                mode = 1
                sse.add_message("Ready to Add/Renew <BR> Swipe again to cancel")
            else:
                cardvisit(card)
        else:
            sse.add_message("Unrecognized Card")
    else:
        if (replcard != ""): 
            if (card not in carddb):
                replacecard(card)
            else:
                sse.add_message("Card already in use")
                return
        elif (card in carddb): 
            if (not carddb[card]["staff"]): 
                renewcard(card)
                sse.add_message(f'Member { membername(card) } <BR> { get_remain(card) } days left')
            else:
                sse.add_message("Cancelled")
        else: 
            memno = addcard(card)
            sse.add_message(f'Member { memno } Created')
        mode = 0
    if adhits == 5:
        sse.add_message("Swipe TWICE more to Shutdown")
    elif adhits == 6:
        sse.add_message("Swipe ONCE more to Shutdown")
    elif adhits == 7:
        sse.add_message("Shutting Down <BR>Power Off when Card Reader Light out")
        threads.stop_threads()
        return

qq=[]
def clearq():
    global qq
    qq = []
def addq(c):
    global qq
    #if len(qq) > 0 and utils.getnow()-qq[0]["dt"] > timedelta(seconds=5):
    #    clearq()        
    if c == "qq":
        clearq()
    elif c[0:1] == "r":
        rcd = c[1:]
        qq.append({"cd": "1","dt": utils.getnow()}) 
        qq.append({"cd": "1","dt": utils.getnow()}) 
        qq.append({"cd": rcd,"repl": True,"dt": utils.getnow()}) 
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

def handlecard(card):
    if len(carddb) == 0:
        addcard(card,True)
        sse.add_message("Master Card Created")
    else:
        addq(card)
        cq=getq()
        if cq == "MMMMMM":
            sse.add_message("Shutdown")
            clearq()
        elif cq == "MMMMM":
            sse.add_message("Swipe ONE more time to Shutdown")
        elif cq == "MMMM":
            sse.add_message("Swipe TWO more times to Shutdown")
        elif cq == "MMM": # special case for shutdown only - we want to NOT clear but put screen back to normal??
            sse.add_message("Swipe THREE more times to Shutdown")
        elif cq == "MMKM":
            card = qq[2]["cd"]
            renewcard(card)
            sse.add_message(f'Member { membername(card) } <BR> { get_remain(card) } days left')
            clearq()
        elif cq[0:3] == "MMK" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
        elif cq == "MMK":
            sse.add_message("Swipe Master to Renew <BR> Any other card will cancel")
        elif cq == "MMUM":
            memno = addcard(qq[2]["cd"])
            sse.add_message(f'Member { memno } Created')
            clearq()
        elif cq[0:3] == "MMU" and len(cq) > 3:
            sse.add_message("Cancelled")
            clearq()
        elif cq == "MMU":
            sse.add_message("Swipe Master to Add - any other card to cancel")
        elif cq == "MMQ":
            if qq[2]["cd"] in carddb:
                sse.add_message(f'Swipe card to replace for { membername(qq[2]["cd"]) }')
            else:
                sse.add_message("Invalid Card - cannot replace")
                clearq()
        elif cq[0:3] == "MMQ" and len(cq) > 3:
            if cq == "MMQU":
                ccd = qq[2]["cd"]
                rcd = qq[3]["cd"]
                sse.add_message(f'Replaced Card for { membername(ccd) }')
                carddb[rcd] = carddb[ccd]
                del carddb[ccd]
            else:
                sse.add_message("Card already in use <BR> Replacement cancelled")
            clearq()
        elif cq == "MM":
            sse.add_message("Add or Renew a Card")
        elif cq == "MK":
            cardvisit(qq[1]["cd"])
            clearq()
        elif cq == "MU" or cq == "U":
            sse.add_message("Unknown Card")
            clearq()
        elif len(cq) == 1:
            cardvisit(qq[0]["cd"])
            if cq[0] == "K":
                clearq()
        else:
            sse.add_message("Ready for Card")
            clearq()

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

@app.route('/update', methods=['POST'])
def update():
    global carddb
    if sysactive:
        card = request.form.get("card")
        if (card in carddb):
            try:
                log.addlog("UpdateBefore",card) 
                carddb[card]["name"] = request.form.get("name")
                carddb[card]["papermemno"] = request.form.get("papermemno")
                carddb[card]["expires"] = utils.check_date(request.form.get("expires"),carddb[card]["expires"])
                try: 
                    carddb[card]["staff"] = request.form.get("staff").lower()=="on"
                except:
                    pass # if not checked we get Nonetype so catch that...
                log.addlog("UpdateAfter",card)
                savedb()
            except Exception as e:
                print(e)
        return "Updated Successfully"
    else:
        return "System Shutting Down"

@app.route('/savepic', methods=['POST'])
def savepic():
    global carddb
    if sysactive:
        card = request.form.get("image")
        with open("imageToSave.png", "wb") as fh:
            imagedata = request.form.get("image")
            imagedata = imagedata.replace("data:image/png;base64,","")
            b64data = base64.b64decode(imagedata)
            fh.write(b64data)
    return("OK")

@app.route('/replace', methods=['POST'])
def replace():
    global replcard, mode
    if sysactive:
        replcard = request.form.get("card")
        mode = 1
        sse.add_message(f'Scan Replacement Card for Member {request.form.get("memno")}')
        return render_template('replace.html')
    else:
        return "System Shutting Down"

@app.route('/stream')
def stream():
    def stream():
        messages = sse.announcer.listen()  
        sse.add_message(f'##Active Members {log.countmember()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)