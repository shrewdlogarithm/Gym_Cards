import os,json,threading,time,re
from collections import OrderedDict
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from queue import Queue
from flask import Flask, Response, request, render_template
from playsound import playsound

sysactive = True

## Messages
import queue
class MessageAnnouncer:
    def __init__(self):
        self.listeners = []
    def listen(self):
        q = queue.Queue(maxsize=5)
        self.listeners.append(q)
        return q
    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]
announcer = MessageAnnouncer()
def format_sse(data: str, event=None) -> str:
    msg = f'data: {data}\n\n'
    if event is not None:
        msg = f'event: {event}\n{msg}'
    return msg
def add_message(m):
    msg = format_sse(data=m)
    announcer.announce(msg=msg)
    print(m)

## Date/Time functions
timeoff = 0
def get_time():
    return datetime.now().date()+timedelta(days = timeoff)
def calc_expiry(card):
    expdate = datetime.strptime(carddb[card]["renew"],dateform)
    while expdate < datetime.now()+relativedelta(days=7):
        expdate = expdate+relativedelta(months=1)
    return expdate.strftime(dateform)
def get_remain(card):
    if card in carddb:
        return max(0,(datetime.strptime(carddb[card]["renew"],dateform).date()-get_time()).days,0)
    else:
        return ""
def check_date(newdate,fbdate):
    try:
        ndate = datetime.strptime(newdate,dateform).strftime(dateform)
        return ndate
    except:
        return fbdate


## Logs
logs = []
def logname():
    return f'logs/gym-{get_time().strftime("%Y%m%d")}.log'
def addlog(ev,card="",db="",excep=""):
    global logs
    newlog = {
        "dt": datetime.now(),
        "offdt": get_time(),
        "event": ev,
        
    }
    if (card != ""):
        newlog["card"] = card
    if (db != ""):
        newlog["db"] = db
    if (excep != ""):
        newlog["excep"] = excep
    logs.append(newlog)
    try:
        with open(logname(),"a") as lf:
            lf.write(json.dumps(newlog,default=str) + ",\n")
    except Exception as e:
        print(f'Log Writing exception {e}')
try:
    if os.path.exists(logname()):
        with open(logname()) as lf:
            listo = lf.read()
            logs = json.loads("[" + listo[0:len(listo)-2] + "]")
except Exception as e:
    addlog("LoadingLogs",excep=e)
    logs = []

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
    addlog("LoadingDB",excep=e)
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
            "created": get_time().strftime(dateform),
            "lastseen": "",
            "renew": get_time().strftime(dateform),
            "memno": memno,
            "papermemno": "",
            "name": ""
        }
        addlog("CardCreate",card)
        savedb()
        return memno
    else:
        return -1 # this should really never happen...
def renewcard(card):
    newexpires = calc_expiry(card)
    carddb[card]["renew"] = newexpires
    addlog("CardRenew",card)
    savedb()
replcard=""
def replacecard(card):
    global replcard
    addlog("CardReplacedOld",replcard)
    carddb[card] = carddb[replcard]
    add_message(f'##Replaced {replcard} with {card} for Member {carddb[card]["memno"]}')
    addlog("CardReplacedNew",card)
    del carddb[replcard]
    replcard = ""
    add_message('Card Replaced')
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
        playsound('./sounds/exp.mp3')
        return "expired"
    elif (gr < 8):
        return "renew"
    else:
        return ""
for log in logs:
    if ("card" in log):
        handlemember(log["card"])

## Threads
thr = []
def start_thread(fn):
    t = threading.Thread(target=fn)
    t.start()
    thr.append(t)
# TODO not currently used?
def stop_threads():
    global sysactive
    sysactive = False
    for t in thr:
        try:
            t.join()
        except:
            pass # self closing the test thread will fail

## Read Cards
cards = Queue()

try: # these are the Pi only card reads - they will fail on desktop

    ## This is the later code for the RC522
    # import RPi.GPIO as GPIO
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setwarnings(False)
    # GPIO.setup(11, GPIO.OUT)	
    # from RC522_Python import RFID
    # rdr = RFID()
    # def readpi():
    #     cn = 0
    #     while sysactive:
    #         rdr.wait_for_tag()
    #         (error, data) = rdr.request()
    #         if not error:
    #             print("\nDetected: " + format(data, "02x"))
    #         (error, uid) = rdr.anticoll()
    #         if not error:
    #             cards.put(":".join([str(id) for id in uid]))
    #             #GPIO.output(11,True)
    #             time.sleep(.2)
    #             GPIO.output(11,False)
    #         time.sleep(.8)
    #start_thread(readpi)
    
    ## This supports your standard RC522 connected to the GPIO as per various online articles...
    #import RPi.GPIO as GPIO
    # from mfrc522 import SimpleMFRC522
    # def read13():
    #     reader = SimpleMFRC522()
    #     while sysactive:
    #         try:
    #             id, text = reader.read()
    #             cards.put(id)
    #         finally:
    #             GPIO.cleanup()
    # #start_thread(read13)

    ## This supports the SB Components RFID Hat
    # import serial  
    # def read125():
    #     def read_rfid():
    #         ser = serial.Serial ("/dev/ttyS0")                           
    #         ser.baudrate = 9600                                          
    #         data = ser.read(12)                                          
    #         ser.close ()                                                 
    #         data=data.decode("utf-8")
    #         return data                                                  
    #     while sysactive:
    #         id = read_rfid ()                                            
    #         cards.put(id)
    #start_thread(read125)

    pass
except: 
    pass

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
                                addlog("evdev_keyevent_exception",excep=e)
            except Exception as e:
                    addlog("evdev_device_exception",excep=e)
    except Exception as e:
        pass # this catches the evdev library exception on Windows    
start_thread(eventinput)

## Keyboard Input (this is mainly here for Windows as there's no evdev input there)
def keyinput():
    global timeoff
    while sysactive:
        try:
            i = input()
            if sysactive:
                off = re.search(r'(\d+)d', i)
                if off:
                    timeoff += int(off.group(1))
                    add_message("##TimeOffset" + off.group(1))
                else:
                    cards.put(i)
        except:
            addlog("KeyInput_exception",excep=e)
start_thread(keyinput)

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
    if adhits == 5:
        add_message("Swipe TWICE more to Shutdown")
    elif adhits == 6:
        add_message("Swipe ONCE more to Shutdown")
    elif adhits == 7:
        add_message("Shutting Down <BR>Power Off when Card Reader Light out")
        stop_threads()
        return
    lastcard = {"card": card,"dt": datetime.now()}
    if (len(carddb) == 0):
        addcard(card,1)
        add_message("Master Card Created")
    elif (mode == 0):
        if (card in carddb):
            if (carddb[card]["level"] > 0):
                mode = 1
                add_message("Ready to Add/Renew <BR> Swipe again to cancel")
            else:
                addlog("MemberInOut",card)
                add_message(f'{membergreet(card) } { membername(card)} <BR> { get_remain(card) } days left:::{ memberstatus(card) }')
                handlemember(card)
                add_message(f'##Active Members {membersonsite()}')
        else:
            add_message("Unrecognized Card")
    else:
        if (replcard != ""): 
            if (card not in carddb):
                replacecard(card)
            else:
                add_message("Card already in use")
                return
        elif (card in carddb): 
            if (carddb[card]["level"] == 0): 
                renewcard(card)
                add_message(f'Member { membername(card) } <BR> { get_remain(card) } days left')
            else:
                add_message("Cancelled")
        else: 
            memno = addcard(card)
            add_message(f'Member { memno } Created')
        mode = 0
def process_cards():
    while sysactive:
        time.sleep(.2) # this avoids thrashing 1 core constantly...
        while (not cards.empty()):
            handle_card(cards.get())            
start_thread(process_cards)

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
            addlog("UpdateBefore",card) # TODO log DB also?
            carddb[card]["name"] = request.form.get("name")
            carddb[card]["papermemno"] = request.form.get("papermemno")
            carddb[card]["renew"] = check_date(request.form.get("renew"),carddb[card]["renew"])
            addlog("UpdateAfter",card)
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
        add_message(f'Scan Replacement Card for Member {request.form.get("memno")}')
        return render_template('replace.html')
    else:
        return "System Shutting Down"

@app.route('/stream')
def stream():
    def stream():
        messages = announcer.listen()  
        add_message(f'##Active Members {membersonsite()}')
        while sysactive:
            msg = messages.get()  
            yield msg
    return Response(stream(), mimetype='text/event-stream')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)