#!/usr/bin/env python\
import cups
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
        
        cups = self.state['cups']
        query = self.query
        
        for key, value in query:
            if key != 'text' & 'barcode' & 'qrcode':
                query.pop(key)
            else:
                data.update({key, value})
        
        
        
        #This logic block is included for barcode implementation in the future, if barcodes are desired.
        if query.has_key('text') & query.has_key('barcode'):
            self.makeFile(query.get('text'),query.get('barcode'))
            if query.has_key('copies'):
                for i in range(0,int(query.get('copies'))):
                    cups.printFile(cups.getDefault(),'temp_print_file', str(i),{})
                    
                self.send_response(200)
                self.send_header("content-type", "text/plain")
                self.end_headers() 
                    
         
    
    
    def do_cmd_info(self):
        self.send_response( 200 )
        self.send_header("content-type", "text/plain")
        self.end_headers()
        info = {"uuid" : self.state["uuid"],
          "status" : self.state["connection"],
          "state" : "",
          "name" : "Zebra GK420t printer"}
        if self.state['connection'] == 'not_connected':
            info.update({"status":"not ready - no CUPS connection"})
        response = json.dumps(info)
        self.wfile.write(response)
        pass
    
    #This makes the file that is sent to the CUPS server
    def makeFile(self, text, barcode):
        if barcode == 'null':
            outfile = open('temp_print_file', 'w')
            outfile.write('\n' + text + '\n')
            
        else:
            #outfile = open('/temp/temp_print_file','w')
            #NEED TO FIGURE OUT HOW TO PRINT BYTES IN PYTHON,
            #CAN GET BYTES FROM BARCODE LIBRARY
            outfile = open('temp_print_file', 'w')
            outfile.write('\n')
            outfile.write(text + '\n')
        pass    
    
class labprinter(basedevice.BaseDevice):
    
    def __init__(self, handler):
        basedevice.BaseDevice.__init__(self, handler)
        self.state['connection'] = 'not_connected'
        while self.state['connection'] != 'connected':
            try:
                self.state['cups'] = cups.Connection()
                self.state['connection'] = 'connected'
            except Exception:
                print 'Initialization failed: unable to establish CUPS connection.'
                print Exception.__doc__
                time.sleep(5)
            
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