import json,re

fobrep = re.compile("[^a-z](fob)", re.IGNORECASE)
brarep = re.compile("[\(\)]")

with open("data/cards.json") as json_file:
    carddb = json.load(json_file)

for card in carddb:
    nm = carddb[card]["name"]
    nmm = nm.replace(carddb[card]["papermemno"],"")
    nfob = ""
    war = ""
    if "fob" in str.lower(nm):
        if "vip" not in carddb[card] or not carddb[card]["vip"]:
            war += "Fob but not VIP? "
    else:
        if "vip" in carddb[card] and carddb[card]["vip"]:
            war += "VIP but not Fob? "
    nmf = fobrep.sub("",nmm)
    fin = nmf.replace("(","")
    fin = fin.replace(")","").strip()
    if any(char.isdigit() for char in fin):
        war += "Old Memno? "
    print("%20s" % nm,"%20s" % nmm,"%20s" % nmf,"%20s" % fin,war)

    #carddb[card]["leename"] = carddb[card]["name"]
    #carddb[card]["name"] = fin

#with open("data/cards.json", 'w') as json_file:
#        json.dump(carddb, json_file, indent=4,default=str)