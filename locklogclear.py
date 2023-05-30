import re,time,json
from pyquery import PyQuery
import utils,lock

with open("data/cards.json") as json_file:
    carddb = json.load(json_file)

updatelock = False # change this to actually remove users from the lock

lockcards = []
un = 1
usersfound=0
lockretry = 3
while lockretry > 0:
    lockretry -= 1
    try:
        page = lock.getpage("ACT_ID_21",{'s2': 'Users'})
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
            if usersfound >= int(pgs[0]): 
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
        break
    except:
        time.sleep(1) # cannot read lock

remc = 0
for card in lockcards:
    card = card.zfill(10)
    print("Lock Card ",card,end="")
    if card in carddb:
        if utils.ismtype(carddb[card],"vip"):
            pass
        else:
            print(" IS NOT VIP - REMOVE",end="")
            remc += 1
            if updatelock: lock.updatelock(card,False)
    else:
        print(" IS NOT IN CardDB - REMOVE",end="")
        remc += 1
        if updatelock: lock.updatelock(card,False)
    print("")
for card in carddb:
    print("DB  Card ",card,end="")
    if card in lockcards:
        if utils.ismtype(carddb[card],"vip"):
            pass
        else:
            print(" IS NOT VIP but in lock - REMOVE",end="")
            if updatelock: lock.updatelock(card,False)
    else:
         if utils.ismtype(carddb[card],"vip"):
            print (" IS VIP but not in lock - ADD",end="")
            if updatelock: lock.updatelock(card,true)
    print("")
print (len(lockcards),"cards in lock",remc,"removed")