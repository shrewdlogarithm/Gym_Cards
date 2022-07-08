import threading

## Threads
thr = []
def start_thread(fn):
    t = threading.Thread(target=fn)
    t.start()
    thr.append(t)
# TODO not currently used?
def stop_threads():
    for t in thr:
        try:
            t.join()
        except:
            pass # self closing the test thread will fail
t = 0
def reset_timeout(to,ktofn):
    global t
    if t or to == 0:
        try:
            t.cancel()
        except:
            pass
    if to != 0:
        t = threading.Timer(to,ktofn,[to])
        t.start()
