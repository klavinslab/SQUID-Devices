"""
Joseph Sullivan
ISTC-PC
Smart Wet lab

--Refrigerator device script--
SQUID compliant basedevice which monitors the temperature and door state of refrigerators/freezers.
The Refrigerator class contains a seperate monitor for each refrigerator monitored by the device.
The number of regrigerators is specified in the construction of the device. Currently 2 is supported, but
this number can be expanded easily"""

#!/usr/bin/env python
import time, traceback, os, sys, spidev, math, json, httplib, urllib, threading
import RPi.GPIO as GPIO
from basedevice import BaseDevice, BaseDeviceRequestHandler

#acquire is a global variable, when acquire is set to true
#the 
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
	global acquire
        if acquire:
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
		acquire = True
            except Exception:
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

    def stop(self):
	self.state["monitor"].stop()
	self.state["monitor"].spi.close() 
	BaseDevice.stop(self)



class refrigerator_monitor(threading.Thread):
    
   # Monitor:
   # Does all of the data collection and if the SQUID is acquiring data from the device
   # then this class will POST data to the squid as it becomes available.
    
    
    def __init__(self, spi_port, in_pin):
	threading.Thread.__init__(self)
        #Device information and SQUID address
        self.is_running = False
        self.is_open = False
	self.in_pin = in_pin
        self.SQUID_IP = ''
        self.SQUID_PORT = ''
        self.uuid = ''
        self.spi = spidev.SpiDev(spi_port,0)
	#self.spi.cshigh = True	
        #Constants used to calculate temperature
        self.Rref = 10000
        self.R = 26560
        self.A1 = 3.354016e-3
        self.B1 = 2.569850e-4
        self.C1 = 2.620131e-6
        self.D1 = 6.383091e-8
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(in_pin,GPIO.IN)
	self.running = True
    
    def run(self):
        count = 0
        
        if GPIO.input(self.in_pin) == True:
            is_open = True
        elif GPIO.input(self.in_pin) == False:
            is_open = False
        
        while self.running:
            self.check_door()
            count += 1
            if count == 10:
                self.read_temperature()
                count = 0
            time.sleep(1)    
         
    def check_door(self):
	#When the door is open, the input pin is logic high
	#hence an open door is high true
        global acquire
	door_state = GPIO.input(self.in_pin)

        if door_state == True:
            if not self.is_open == True:
                if acquire:
                    self._post_squid_data({"event-type" : "opened","time" : time.time()})
                self.is_open = True

        elif door_state == False:
            if not self.is_open == False:
                if acquire:
                    self._post_squid_data({"event-type" : "closed","time" : time.time()})
                self.is_open = False
 
    def read_temperature(self):
        global acquire

        values = self.spi.xfer2([1,8<<4,0])
        value = ((values[1]&3) << 8) + values[2]

        v = 3.31*value/1024
        x = ((self.R * v)/(3.31 - v))//self.Rref
        T = 1/(self.A1 + self.B1*math.log(x) + self.C1*math.pow(math.log(x),2) + self.D1*math.pow(math.log(x),3))
	
        if acquire:
            self._post_squid_data({"temperature" : T,"time": time.time()})
            
    def acquire(self, uuid, ip, port):
        self.uuid = uuid
        self.SQUID_IP = ip
        self.SQUID_PORT = port
        
    def _post_squid_data(self,data):
        print 'posting data to squid'

        d = {"datum[uuid]": self.uuid,
             "datum[data]": data}
        print d

        post_data = urllib.urlencode(d)

       # headers = {"Content-type": "application/x-www-form-urlencoded",
       #            "Accept": "text/plain"}

        conn = httplib.HTTPConnection(self.SQUID_IP, \
                                      self.SQUID_PORT)
       # conn.request("POST",post_data,headers)
	conn.request("POST", '/data', post_data)

    def stop(self):
	self.running = False

        
def make_pid():
    pid = os.getpid()
    if os.path.exists("/var/run/scale.pid"):        #This process is already running on the machine. Stop execution
        raise Exception
    outfile = open("/var/run/refrigerator.pid" , 'w') #Build the PID file that identifies this process
    outfile.write(str(pid) + '\n')        



        
if __name__ == '__main__':
    if os.path.exists("/var/run/refrigerator.pid"):
	print "Process is already running."
	sys.exit()

    try:
        make_pid()
        dev = Refrigerator(RefrigeratorRequestHandler,None,0,25)
        dev.start()
        dev.state['monitor'].start()

        while os.path.exists("/var/run/refrigerator.pid"):
	    try:
                if not dev.state['monitor'].isAlive():
                    break
                time.sleep(10)                          #Keep executing, check again in 10 seconds
	    except KeyboardInterrupt:
	        raise Exception       

        if os.path.exists("/var/run/refrigerator.pid"):
            os.remove("/var/run/refrigerator.pid")	#cleanup the PID
    
        dev.stop()
	GPIO.cleanup()

    except Exception:        				
		                                               #Something has gone wrong, break down the program
        print "BREAKING DOWN PROGRAM"
	traceback.print_exc()
	dev.stop()
        GPIO.cleanup()
	if os.path.exists("/var/run/refrigerator.pid"):
		os.remove("/var/run/refrigerator.pid")
   

