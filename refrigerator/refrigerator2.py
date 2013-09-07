#!/usr/bin/env python
import time, traceback, os, sys, spidev, math, json, httplib, urllib
import RPI.GPIO as GPIO
from basedevice import BaseDevice, BaseDeviceRequestHandler
from threading import Thread

acquire = False

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

                self.send_response(200)
                self.send_header("content-type", "text/plain")
                self.end_headers()
                self.wfile.write("OK")
                self.state["SQUID-IP"] = self.client_address[0];
                self.state["SQUID-PORT"] = self.query["port"]                
                self.state["monitor"].acquire(self.state['uuid'], self.state['SQUID-IP'], self.state['SQUID-PORT'])
            except Exception:
                #SOMETHING WENT WRONG! HO-LI-****
                print 'exception caught in do_cmd_acquire'
                self.send_response(500)
                self.send_header("content-type","text/plain")
                self.end_headers()
                self.wfile.write("Get Joey to fix it")
                traceback.print_exc()
                raise Exception
        
    
        
class Refrigerator(BaseDevice):
    """
    BaseHttpDevice
    spi_port is the channel used for serial peripherial comm.
    Inputs:
        in_pin is the GPIO pin (named by BCM convention) that is used to monitor
            the state of the door. High voltage -> Logic True -> Door is Open
    """
    
    def __init__(self, handler, settings, spi_port, in_pin):
        BaseDevice.__init__(self, handler)
        self.settings = settings
        self.state['monitor'] = refrigerator_monitor(spi_port, in_pin)
        print 'refrigerator device constructed'
            
    def update_time_forever(self):
        self.state["time"] = time.time()
        time.sleep(1)

class refrigerator_monitor(Thread):
    """
    Monitor:
    Does all of the data collection and if the SQUID is acquiring data from the device
    then this class will POST data to the squid as it becomes available.
    """
    
    def __init__(self, spi_port, in_pin):
        #Device information and SQUID address
        self.is_running = False
        self.is_open = False
        self.SQUID_IP = ''
        self.SQUID_PORT = ''
        self.uuid = ''
        self.spi = spi.SpiDev(spi_port,0)
        #Constants used to calculate temperature
        self.Rref = 10000
        self.R = 25500
        self.A1 = 3.354016e-3
        self.B1 = 2.569850e-4
        self.C1 = 2.620131e-6
        self.D1 = 6.383091e-8
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(in_pin,GPIO.IN)
        threading.Thread.__init__(self)
    
    def run(self):
        self.running = True
        count = 0
        #Set state of the door
        if GPIO.input(self.in_pin) == True:
            is_open = True
        elif GPIO.input(self.in_pin) == False:
            is_open = False
        #running loop
        while self.running:
            print "running loop"
            self.check_door()
            count += 1
            if count == 10:
                self.read_temperature()
                count = 0
            time.sleep(1)    
          
    def  check_door(self):
        global acquire
        if GPIO.input(self.in_pin) == True:
            if not is_open == True:
                if acquire:
                    self._post_squid_data({"event-type" : "opened","time" : datetime.time})
                is_open = True
        elif GPIO.input(self.in_pin) == False:
            if not is_open == False:
                if acquire:
                    self._post_squid_data({"event-type" : "closed","time" : datetime.time})
                is_open == False
    
    def read_temperature(self):
        global acquire
        values = self.spi.xfer2([1,8<<4,0])
        value = ((values[1]&3) << 8) + values[2]
        v = 3.31*value/1024
        x = ((self.R * v)/(3.31 - v))/self.R
        T = 1/(self.A1 + self.B1*math.log(x) + self.C1*math.pow(math.log(x),2) + self.D1*math.pow(math.log(x),3))
        if acquire:
            self._post_squid_data({"temperature" : T,"time": datetime.time})
            
    def acquire(self, uuid, ip, port):
        global acquire
        self.uuid = uuid
        self.SQUID_IP = ip
        self.SQUID_PORT = port
        acquire = True
    
        
    def _post_squid_data(self,data):
        print 'posting data to squid'
        d = {"datum[uuid]": self.uuid,
             "datum[data]": data}
        print d
        post_data = urllib.urlencode(d)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.SQUID_ID, \
                                      self.SQUID_PORT)
        conn.request("POST",post_data,headers)
        
def make_pid():
    pid = os.getpid()
    if os.path.exists("/var/run/scale.pid"):        #This process is already running on the machine. Stop execution
        raise Exception
    outfile = open("/var/run/refrigerator.pid" , 'w')
    outfile.write(str(pid) + '\n')        
        
if __name__ == '__main__':
    try:
        make_pid()
        dev = Refrigerator(RefrigeratorRequestHandler,None,0,25)
        dev.state['monitor'].start()
        print 'threads have been started'
        while os.path.exists("/var/run/refrigerator.pid"):
            time.sleep(10)                          #Keep executing, check again in 10 seconds
    except Exception:                               #Something has gone wrong, break down the program
        crashlog = '/home/bioturk/SQUID-Devices/crashlog_' + str(time.time(),'w')
        outfile = open(crashlog)
        outfile.write(traceback.print_exc())
        print 'Crashlog \t' + crashlog
        if os.path.exists("var/run/refrigerator.pid"):
            os.remove("/var/run/refrigerator.pid")  #cleanup the PID
        try:
            self.state["doorwatcher"].stop()        #Stop running threads
            self.state["doorwatcher"].stop()
        except Exception:
            print traceback.print_exc()
        sys.exit()
            
    