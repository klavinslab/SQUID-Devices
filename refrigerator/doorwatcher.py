#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
import threading
import datetime
import httplib, urllib
import json

"""
doorwatcher is a thread which monitors open/close events on the door and then posts
this data to the SQUID
"""
class DoorWatcher(threading.Thread):
    
    def __init__(self, in_pin):
        self.uuid = ''
        self.SQUID_IP = ''
        self.SQUID_PORT = ''
        self.running = False
        self.acquire = False
        self.in_pin = in_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(in_pin,GPIO.IN)
        threading.Thread.__init__(self)
        print 'doorwatcher has been constructed'

        
    def run(self):
        print 'doorwatcher is running'
        self.running = True
        #Initialize state of the door
        if GPIO.input(self.in_pin) == True:
            is_open = True
        elif GPIO.input(self.in_pin) == False:
            is_open = False
        #Every second check the state of the door, and if its state has changed post the event to SQUID        
        while self.running == True:
            if GPIO.input(self.in_pin) == True:
                if not is_open == True:
                    if self.acquire:
                        self._post_squid_data({"event-type" : "opened","time" : datetime.time})
                    is_open = True
            elif GPIO.input(self.in_pin) == False:
                if not is_open == False:
                    if self.acquire:
                        self._post_squid_data({"event-type" : "closed","time" : datetime.time})
                    is_open == False
            time.sleep(1)
    
    def _post_squid_data(self,data):
        print 'posting squid data'
        d = {"datum[uuid]": self.uuid,
             "datum[data]": data}
        print d
        post_data = urllib.urlencode(d)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.SQUID_ID, \
                                      self.SQUID_PORT)
        conn.request("POST",post_data,headers)
      
    def stop(self):
        self.running = False
    
    def acquire(self, uuid, ip, port):
        print 'doorwatcher is acquiring'
        self.uuid = uuid
        self.SQUID_IP = ip
        self.SQUID_PORT = port
        self.acquire = True
    
    

