import json,log
import utils
from glob import glob

def loadlogs(connection):
    try:
        connection.execute("DROP TABLE LOGS;")
        connection.execute("CREATE TABLE LOGS (dt TEXT NOT NULL,memno INTEGER, event TEXT NOT NULL, card TEXT NOT NULL, db TEXT, excep TEXT);")
        connection.execute("CREATE INDEX LOGS_event_dt ON LOGS (event,dt);")
        connection.execute("CREATE INDEX LOGS_dt ON LOGS (dt) ;")
        connection.execute("CREATE INDEX LOGS_memno ON LOGS (memno);")

        lfiles = glob(f"./logs/{utils.sett['systemname']}-*.log") # ignores lockacces.log
        for file in lfiles:
            with open(file) as lf:
                listo = lf.read()
                listo = listo.replace("\x00","")
                try: 
                    logs = json.loads("[" + listo[0:len(listo)-2] + "]")
                    for log in logs:
                        if log["event"] != "evdev_device_exception": # weirdo event we want to ignore??
                            try:
                                memno = None
                                if "memno" in log["db"]:
                                    memno = log["db"]["memno"]
                                connection.execute("INSERT INTO LOGS (dt,memno,event,card,db,excep) VALUES(?,?,?,?,?,?)",(log["dt"],memno,log["event"],log["card"],json.dumps(log["db"]),log["excep"]))
                            except Exception as e:
                                print(log,e)
                                raise Exception
                except Exception as e:
                    print(file,e)
        connection.commit()
    except Exception as e:
        print(e)

loadlogs(log.connection)