import threading,os

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
            print(t)
            t.join()
        except:
            pass # self closing the test thread will fail
    print("stopped")
t = 0
def reset_timeout(to,ktofn):
    global t
    if t:
        try:
            t.cancel()
        except:
            pass
    t = threading.Timer(to,ktofn,[to])
    t.start()
