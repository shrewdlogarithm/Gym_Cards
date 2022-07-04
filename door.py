client = False
ip_address = "192.168.1.143"
controller_serial = 123209978
try:
    from rfid import RFIDClient
    client = RFIDClient(ip_address, controller_serial)
except: 
    pass

def addlock(card):
    try:
        if client:
            client.add_user(int(card), [1]) 
        else:
            pass
    except Exception as e:
        raise e

def remlock(card):
    try:
        if client:
            client.remove_user(int(card))
        else:
            pass
    except Exception as e:
        raise e

from datetime import datetime
from pyquery import PyQuery
import re,json
import requests
from requests.structures import CaseInsensitiveDict

headers = CaseInsensitiveDict()
headers["Cookie"] = "username=abc; pwd=654321"
