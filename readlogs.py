import os,json,socket
import log,utils

memcountdb = {}
dtparms = ["%Y","%m","%d","%H"]
def inc(memdb,dt,i,amt):
    if dt.strftime(dtparms[i]) not in memdb:
        if i < len(dtparms)-1:
            memdb[dt.strftime(dtparms[i])] = {}
        else:
            memdb[dt.strftime(dtparms[i])] = 0
    if i < len(dtparms)-1:
        inc(memdb[dt.strftime(dtparms[i])],dt,i+1,amt)
    else:
        memdb[dt.strftime(dtparms[i])] += amt

for file in os.listdir("logs"):
    if file.endswith(".log"):
        try:
            with open("logs/" + file,'r') as f:
                lf = f.read()
                logs = json.loads("[" + lf[0:len(lf)-2] + "]")
                memdb = {}
                for log in logs:
                    if log["event"] == "MemberInOut":
                        memno = log["db"]["memno"]
                        dt = utils.getdatelong(log["dt"])
                        if memno not in memdb or not memdb[memno]:
                            memdb[memno] = True
                        else:
                            memdb[memno] = False
                        if memdb[memno]:
                            inc(memcountdb,dt,0,1)
                        else:
                            inc(memcountdb,dt,0,-1)
                print(memcountdb)
        except Exception as e:
            print("Failed reading " + file)
            print(e)