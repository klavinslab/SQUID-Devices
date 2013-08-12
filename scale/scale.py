#!/usr/bin/env python
import serial as pyserial
from threading import Thread
import thread
import time
import datetime
import json
import httplib, urllib
import traceback
import math
import sys
from basedevice import BaseDevice
from basedevice import BaseDeviceRequestHandler
from serial.serialutil import SerialException

#mass of the last read in grams
current_value = 0
#tolerance helps prevent redundant mass readings
tolerance = 0.01
#tare flag helps prevent redundant TARE readings
tare_flag = False
#acquire determines whether or not to post data
acquire = False
#basedevice state object
squid_ip = ''
squid_port = ''

class ScaleRequestHandler(BaseDeviceRequestHandler):

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
                "name"  : "scale"}
        response = json.dumps(info)
        self.wfile.write(response)
        
    def do_cmd_acquire(self):
        global acquire
        global squid_ip
        global squid_port
        
        self.state["SQUID-IP"] = self.client_address[0];
        self.state["SQUID-PORT"] = self.query["port"]
        self.send_response(200)
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.wfile.write("OK")
        acquire = True
        squid_ip = self.state["SQUID-IP"]
        squid_port = self.state["SQUID-PORT"]
        
        print "tried stuff"
        
    
class serialReader(Thread):
    """ the run method of this thread checks the serial connection during each execution of its loop."""
    def run(self):
        global acquire
        powered_on = True
        while self.is_running:
            #line = self.serial.readline()
            #if len(line) > 3:
                #parse_data(line)
            time.sleep(.1)
            try:
                if self.serial.isOpen():
                    if not powered_on:
                        powered_on = True
                        #Powered on event!
                        print "powered on"
                        if acquire:
                            post({"time"      : time.time(),
                                  "event-type": "powered on"})
                    self.read()
                else:
                    self.serial.open()
            except Exception:
                #If this exception is raised then the device is probably off.
                self.serial.close()
                if powered_on:
                    powered_on = False
                    print "powered off"
                    if acquire:
                        post({"time"      : time.time(),
                                  "event-type": "powered off"})
            
    def read(self):
        try:
            line = self.serial.readline()
            if len(line) > 3:
                parse_and_post_data(line)
        except SerialException:
            raise Exception

    
    
    def __init__(self, device, baud):
        Thread.__init__(self)
        self.is_running = False
        while not self.is_running:
            try:
                self.serial = pyserial.Serial(port=device,baudrate=baud)
                self.is_running = True
                print "device (scale) has been found..."
            except SerialException:
                time.sleep(1)

class Scale(BaseDevice):
    def __init__(self, handler):
        global state
        try:
            BaseDevice.__init__(self,handler)
            state = self.state
        except Exception:
            #gonna need a stack trace to figure out what went wrong
            traceback.print_exc()

def parse_and_post_data(line):
    """Parses data from scale"""
    global current_value
    global tolerance
    global tare_flag
    global acquire
    code = line[0:2]
    sign = line [5]
    value = line[9:-5]  

    try:
        while 1:
            value.remove(' ')
    except Exception:
        #Add a trailing zero, this helps prevent an error on startup
        line += '0'
            
    if value.__contains__('L'):
        if not tare_flag:
            print "TARE"
            tare_flag = True  
    elif code == 'ST':
        
        if tare_flag:
            tare_flag = False
            
        if sign == '+':
            value = float(value)
            
        elif sign == '-':
            value = -1 * float(value)
            
        if math.fabs(value - current_value) > tolerance:
            current_value = value
            print current_value
            if acquire:
                post({"time"      :time.time(),
                      "event-type":"stable",
                      "mass"      : current_value})
                pass
        
"""Posts data to SQUID"""
def post(data):
    global squid_ip
    global squid_port
    print "Posting, baby!"
    d = {"datum[uuid]": state["uuid"],
         "datum[data]": data}
    post_data = urllib.urlencode(d)
    print post_data
    
    headers = {"content-type"   : "plain/text",
               "Content-Length" : str(len(json.dumps(d))),
                "Accept"        : "text/plain"}
    
    conn = httplib.HTTPConnection(squid_ip, \
                                      squid_port)
    conn.request("POST",'/data',post_data,headers)   

            
if __name__ == '__main__':
    try:
        dev = Scale(ScaleRequestHandler)
        serial = serialReader('/dev/ttyUSB0',9600)
        serial.start()
        dev.start()
        raw_input ('Press anything to stop this madness!\n')
        dev.stop()
    except Exception:
        traceback.print_ex

