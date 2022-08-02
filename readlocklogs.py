from pyquery import PyQuery
import re,time,requests
#lock = 'http://127.0.0.1'
lock = 'http://192.168.1.143'

rs = requests.session()

def getpage(path,vars={}):
    return rs.post(lock + "/" + path, headers={'Content-Type': 'application/x-www-form-urlencoded','referer': "192.168.1.143"}, data = vars, timeout=1)

un = 1
page = getpage("ACT_ID_21",{'s4': 'Swipe'})
while 1==1:
    recid2 = 0
    pgs = re.findall(r"Page[^0-9]+?([0-9]+)[^0-9]+?Of[^0-9]+?([0-9]+)[^0-9]+?Page",page.text)
    pq = PyQuery(bytes(bytearray(page.text, encoding='utf-8')))
    for row in pq("table:last tr"):
        cells = []
        for cell in PyQuery(row)("td"):
            cells.append(cell)
        if len(cells):
            if recid2 == 0:
                recid2 = int(cells[0].text)-1
            print([cells[0].text,cells[1].text,cells[2].text,cells[3].text,cells[4].text])
    if int(pgs[0][0]) == int(pgs[0][1]):
        break
    else:
        while 1==1:
            try:
                print("Trying to read page ", un)
                if page:
                    page.close()
                page = getpage("ACT_ID_345",{
                    "PC":recid2,
                    "PE":"0",
                    "PN":"Next"})
                un += 1
                break
            except Exception as e:
                print("Failed with ", e)
                time.sleep(1)
    time.sleep(0)