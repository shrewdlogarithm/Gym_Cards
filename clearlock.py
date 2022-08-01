from pyquery import PyQuery
import re,time,json,requests
lock = 'http://192.168.1.143'

def getpage(path,vars={}):
    return requests.post(lock + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': "192.168.1.143"}, data = vars, timeout=1).text

# Read all Users
lockcards = []
un = 1
page = getpage("ACT_ID_21",{'s2': 'Users'})
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
    if usersfound >= int(pgs[0]):
        break
    else:
        try:
            page = getpage("ACT_ID_325",{
                "PC":"{:05d}".format((un-1)*20+1),
                "PE":"{:05d}".format(un*20),
                "PN":"Next"})
        except:
            break
        un += 1
        time.sleep(1)

with open("data/cards.json") as json_file:
    carddb = json.load(json_file)

for card in lockcards:
    print("Lock Card ",card,end="")
    if card in carddb:
        print("in CardDB",end="")
        if "vip" in carddb[card] or carddb[card]["vip"]:
            print("Is VIP",end="")
        else:
            print("NOT VIP - REMOVE",end="")
    else:
        print("NOT IN CardDB - REMOVE",end="")
    print("")