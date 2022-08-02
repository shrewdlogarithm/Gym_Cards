import re,time,json
from pyquery import PyQuery
import lock
lock_address = "192.168.1.143"
controller_serial = 123209978

with open("data/cards.json") as json_file:
    carddb = json.load(json_file)

# Read all Users
lockcards = []
un = 1
page = lock.getpage("ACT_ID_21",{'s2': 'Users'})
usersfound=0
while 1==1:
    pgs = re.findall(r"Total Users: ([0-9]+)",page)
    pq = PyQuery(bytes(bytearray(page, encoding='utf-8')))
    for row in pq("table:last tr"):
        cells = []
        for cell in PyQuery(row)("td"):
            cells.append(cell)
        if len(cells):
            lockcards.append(cells[1].text)
            usersfound += 1
    if usersfound >= int(pgs[0]): # TODO THIS LINE SOMETIMES FAILS???
        break
    else:
        try:
            page = lock.getpage("ACT_ID_325",{
                "PC":"{:05d}".format((un-1)*20+1),
                "PE":"{:05d}".format(un*20),
                "PN":"Next"})
        except:
            break
        un += 1
        time.sleep(1)

remc = 0
for card in lockcards:
    card = card.zfill(10)
    print("Lock Card ",card,end="")
    if card in carddb:
        print(" IS in CardDB",end="")
        if "vip" in carddb[card] and carddb[card]["vip"]:
            print(" IS VIP",end="")
        else:
            print(" IS NOT VIP - REMOVE",end="")
            remc += 1
            lock.updatelock(card,False)
    else:
        print(" IS NOT IN CardDB - REMOVE",end="")
        remc += 1
        lock.updatelock(card,False)
    print("")
print (len(lockcards),"cards in lock",remc,"removed")