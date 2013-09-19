#!/usr/bin/env python\
import json
import basedevice
import time
import thread
import os
import traceback
import barcode
from barcode.writer import ImageWriter
from subprocess import call
from Label import Label
"""
Programmer: Joseph Sullivan
Research Assistant, ISTC PC

PrintRequestHandler and Labprinter are classes which subclass BaseDevice and BaseDeviceRequestHandler
the device has two possible commands: info and print. Print in turn has three possible fields: 'text', 'barcode'
and 'copies'. Barcode has yet to be implemented.

TODO: in next version create methods that format the document which will be printed so that text wraps properly."""


class PrinterRequestHandler(basedevice.BaseDeviceRequestHandler):
    #code
    
    def do_cmd_print(self):      
        query = self.query
        label = Label(query)
        del label
        if query.has_key('copies'):
            for i in range(0, int(query.get('copies'))):
                os.system('lp -o fit-to-page label.png')
        else:
            os.system('lp -o fit-to-page label.png')
            self.send_response( 200 )
        self.send_header("content-type", "text/plain")
        self.end_headers()        
        self.wfile.write("OK")
        
    def do_cmd_test(self):
        self.send_response( 200 )
        self.send_header("content-type", "text/plain")
        self.end_headers()
        response = "path: " + self.path + "\n"
        response += "qs: " + str(self.query) +"\n"
        response += "post data: " + str(self.postdata) + "\n"
        response += "server data: " + str(self.server.server_address) + "\n"
        response += "server_obj data: " + str(self.state) + "\n"
        response += "clined address: " +str(self.client_address) + "\n"
        self.wfile.write(response)
         
    def do_cmd_info(self):
        self.send_response( 200 )
        self.send_header("content-type", "text/plain")
        self.end_headers()
        info = {"uuid" : self.state["uuid"],
          "state" : "",
          "name" : "Zebra GK420t printer"}
        if self.state['connection'] == 'not_connected':
            info.update({"status":"not ready - no CUPS connection"})
        response = json.dumps(info)
        self.wfile.write(response)  
    
class labprinter(basedevice.BaseDevice):
    
    def __init__(self, handler):
        basedevice.BaseDevice.__init__(self, handler)
            
    def work(self):
        while 1:
            #What should we do?
            #How about we check to see that there are still printers connected?
            time.sleep(5)
        
def make_pid():
    pid = os.getpid()
    outfile = open("/var/run/labprinter.pid" , 'w')
    outfile.write(str(pid) + "\n")

if __name__ == '__main__':
    try:   
        make_pid()
        PORT = 8000
        dev = labprinter(PrinterRequestHandler)
        dev.start()
        while os.path.exists("/var/run/labprinter.pid"):
            time.sleep(10)                              #Keep executing, check again in 10 seconds
        dev.stop()
    except Exception:                                   #Something went wrong, break down the program
        outfile = open("/home/bioturk/SQUID-Devices/LabPrinter/crash_log_" + str(time.time), 'w')
        outfile.write(traceback.print_exc())
        if os.path.exists("var/run/labprinter.pid"):
            os.remove("/var/run/labprinter.pid")      #cleanup the PID
        try:
            dev.stop()                                  #Stop running threads
        except Exception:
            pass