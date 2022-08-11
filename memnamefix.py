import json

def membername(card):
    memname = ""
    if (carddb[card]["name"] != ""):
        memname = carddb[card]["name"]
    elif (carddb[card]["staff"]):
        memname = "Staff-" + str(carddb[card]["memno"])
    else:
        memname = "Member-" + str(carddb[card]["memno"])
    if ("papermemno" in carddb[card] and carddb[card]["papermemno"] != ""):
        memname += " (" + carddb[card]["papermemno"] + ")"
    if ("vip" in carddb[card] and carddb[card]["vip"]):
        memname += " [Fob]"
    return memname

with open("data/cards.json") as json_file:
    carddb = json.load(json_file)

vipc = 0
for card in carddb:
    nm = carddb[card]["name"].lower()
    nmm = nm.replace(carddb[card]["papermemno"].lower(),"")
    nfob = ""
    war = ""
    if "fob" in nm:
        if "vip" not in carddb[card] or not carddb[card]["vip"]:
            war += "Fob but not VIP? "
    else:
        if "vip" in carddb[card] and carddb[card]["vip"]:
            war += "VIP but not Fob? "
    nmf = nmm.replace("fob","")
    fin = nmf.replace("(","")
    fin = fin.replace(")","").strip()
    if any(char.isdigit() for char in fin):
        war += "Old Memno? "
    fin = fin.title()

    if "vip" in carddb[card] and carddb[card]["vip"]:
        vipc += 1

    carddb[card]["papermemno"] = carddb[card]["papermemno"].upper()
    carddb[card]["leename"] = carddb[card]["name"]
    carddb[card]["name"] = fin

    print("%20s" % nm,"%20s" % nmm,"%20s" % nmf,"%20s" % fin,"%30s" % membername(card),war)

print("Total cards",len(carddb)," of which ",vipc,"are VIPs")
#with open("data/cards.json", 'w') as json_file:
#        json.dump(carddb, json_file, indent=4,default=str)