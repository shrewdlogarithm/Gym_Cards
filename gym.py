import os,json,time
from collections import OrderedDict
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from queue import Queue
from flask import Flask, Response, request, render_template
from playsound import playsound
import sse,log,threads

sysactive = True

## Database
dbname = "data/cards.json"
carddb = OrderedDict()
dateform = '%Y-%m-%d' # the format Chrome requires...
def savedb():
    with open(dbname, 'w') as json_file:
        json.dump(carddb, json_file, indent=4,default=str)
        
try:
    if os.path.exists(dbname):
        with open(dbname) as json_file:
            carddb = json.load(json_file)
except:
    log.addlog("LoadingDB",excep=e)
    carddb = {}

#Handle Cards
def addcard(card,level=0):
    global carddb
    if (card not in carddb):
        memno = 0
        for c in carddb:
            if (int(carddb[c]["memno"]) > memno):
                memno = int(carddb[c]["memno"])
        memno += 1
        carddb[card] = {
            "level": level,
            "created": datetime.now().strftime(dateform),
            "lastseen": "",
            "renew": (datetime.now()+relativedelta(months=1)).strftime(dateform),
            "memno": memno,
            "papermemno": "",
            "name": ""
        }
        log.addlog("CardCreate",card)
        savedb()
        return memno
    else:
        return -1 # this should really never happen...
def renewcard(card):
    newexpires = calc_expiry(card)
    carddb[card]["renew"] = newexpires
    log.addlog("CardRenew",card)
    savedb()
def calc_expiry(card):
    expdate = datetime.strptime(carddb[card]["renew"],dateform)
    oexpdate = expdate
    while expdate < datetime.now() or expdate-oexpdate < timedelta(days=28):
        expdate = expdate+relativedelta(months=1)
    return expdate.strftime(dateform)
def get_remain(card):
    if card in carddb:
        return max(0,(datetime.strptime(carddb[card]["renew"],dateform).date()-datetime.now().date()).days+1,0)
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
memdb = {}
def handlemember(card):
    if (card in carddb and carddb[card]["level"] == 0):
        memno = carddb[card]["memno"]
        if memno in memdb:
            del memdb[memno]
        else:
            memdb[memno] = True
def membersonsite():     
    return len(memdb)
def membername(card):
    if (carddb[card]["name"] != ""):
        return carddb[card]["name"]
    elif (carddb[card]["papermemno"] != ""):
        return carddb[card]["papermemno"]
    else:
        return "Member" + str(carddb[card]["memno"])
def membergreet(card):
    if card in carddb:
        if (carddb[card]["memno"] in memdb):
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
    except Exception as e:
        pass # this catches the evdev library exception on Windows    
threads.start_thread(eventinput)

## Keyboard Input (this is mainly here for Windows as there's no evdev input there)
def keyinput():
    while sysactive:
        try:
            cards.put(i)
        except Exception as e:
            log.addlog("KeyInput_exception",excep=e)
threads.start_thread(keyinput)

## Process Cards
mode = 0
lastcard = {"card": -1}
adhits = 0
def handle_card(card):
    global mode,lastcard,adhits
    if (lastcard["card"] in carddb and datetime.now()-lastcard["dt"] < timedelta(seconds=5) and card in carddb and carddb[lastcard["card"]]["level"] != 0 and carddb[card]["level"] != 0):
        adhits += 1
    else:
        adhits = 0
    lastcard = {"card": card,"dt": datetime.now()}
    if (len(carddb) == 0):
        addcard(card,1)
        sse.add_message("Master Card Created")
    elif (mode == 0):
        if (card in carddb):
            if (carddb[card]["level"] > 0):
                mode = 1
                sse.add_message("Ready to Add/Renew <BR> Swipe again to cancel")
            else:
                log.addlog("MemberInOut",card)
                sse.add_message(f'{membergreet(card) } { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
                handlemember(card)
                sse.add_message(f'##Active Members {membersonsite()}')
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
            if (carddb[card]["level"] == 0): 
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
def process_cards():
    while sysactive:
        time.sleep(.2) # this avoids thrashing 1 core constantly...
        while (not cards.empty()):
            handle_card(cards.get())            
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
    def check_date(newdate,fbdate):
        try:
            ndate = datetime.strptime(newdate,dateform).strftime(dateform)
            return ndate
        except:
            return fbdate
    if sysactive:
        card = request.form.get("card")
        if (card in carddb):
            log.addlog("UpdateBefore",card) 
            carddb[card]["name"] = request.form.get("name")
            carddb[card]["papermemno"] = request.form.get("papermemno")
            carddb[card]["renew"] = check_date(request.form.get("renew"),carddb[card]["renew"])
            log.addlog("UpdateAfter",card)
            savedb()
        return "Updated Successfully"
    else:
        return "System Shutting Down"

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
        messages = announcer.listen()  
        sse.add_message(f'##Active Members {membersonsite()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)