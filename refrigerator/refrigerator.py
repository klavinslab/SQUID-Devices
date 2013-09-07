#!/usr/bin/env python
import datetime
import json
import httplib, urllib
from basedevice import BaseDevice, BaseDeviceRequestHandler
from tempwatcher import tempwatcher
from doorwatcher import DoorWatcher
import time
import traceback
import os

class RefrigeratorRequestHandler(BaseDeviceRequestHandler):
    def do_cmd_test(self):
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.end_headers()
        
        response = "path: " + self.path + "\n"
        response += "qs: " + str(self.query) + "\n"
        response += "post data: " + str(self.postdata) + "\n"
        response += "server_obj data: " + str(self.state) + "\n"
        response += "clined address: " + str(self.client_address) + "\n"
        
        self.wfile.write(response)
    
    def do_cmd_info(self):
        self.send_response( 200 )
        self.send_header('content-type', "text/plain")
        self.end_headers()
        info = {"uuid"  : self.state["uuid"],
                "status": "ready",
                "state" : "",
                "name"  : "refrigerator"}
        response = json.dumps(info)
        self.wfile.write(response)
        
    def do_cmd_acquire(self):
        if self.state["acquire"]:
            pass
        else:
            try:
                self.state["tempwatcher"].acquire(self.state['uuid'], self.state['SQUID-IP'], self.state['SQUID-PORT'])
                self.state["doorwatcher"].acquire(self.state['uuid'], self.state['SQUID-IP'], self.state['SQUID-PORT'])
                self.send_response(200)
                self.send_header("content-type", "text/plain")
                self.end_headers()
                self.wfile.write("OK")
                self.state["SQUID-IP"] = self.client_address[0];
                self.state["SQUID-PORT"] = self.query["port"]
            except Exception:
                #SOMETHING WENT WRONG! HO-LI-****
                self.send_response(500)
                self.send_header("content-type","text/plain")
                self.end_headers()
                self.wfile.write("Get Joey to fix it")
        
    
        
class refrigerator(BaseDevice):
    def __init__(self, handler, settings,door_input_pin):
        BaseDevice.__init__(self, handler)
        self.settings = settings
        self.state["acquire"] = False
        self.state['doorwatcher'] = DoorWatcher(door_input_pin)
        self.state['tempwatcher'] = TempWatcher(0)
            
    def update_time_forever(self):
        self.state["time"] = time.time()
        time.sleep(1)      
        
def make_pid():
    pid = os.getpid()
    if os.path.exists("/var/run/scale.pid"):        #This process is already running on the machine. Stop execution
        raise Exception
    outfile = open("/var/run/refrigerator.pid" , 'w')
    outfile.write(str(pid) + '\n')        
        
if __name__ == '__main__':
    try:
        make_pid()
        dev = refrigerator(RefrigeratorRequestHandler,None,25)
        dev.state['doorwatcher'].start()
        dev.state['tempwatcher'].start()
        while os.path.exists("/var/run/refrigerator.pid"):
            time.sleep(10)                          #Keep executing, check again in 10 seconds
    except Exception:                               #Something has gone wrong, break down the program
        outfile = open("/home/bioturk/SQUID-Devices/crash_log_" + str(time.time()), 'w')
        outfile.write(traceback.print_exc())
        if os.path.exists("var/run/refrigerator.pid"):
            os.remove("/var/run/refrigerator.pid")  #cleanup the PID
        try:
            self.state["doorwatcher"].stop()        #Stop running threads
            self.state["doorwatcher"].stop()
        except Exception:
            pass
            
    