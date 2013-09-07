#!/usr/bin/env python
import threading
import time
import datetime
import math
import spidev


#This subprogram monitors the temperature every minute and then returns the
#analog value of the temperature to the refrigerator program, which then writes the data to the SQUID.

#This subprogram reads data using the Raspberry Pi's SPI interface. The SPI interface returns
#a integer value between 0 and 1024, representing the ratio of the voltage drop across the thermometer
#to the 3.3 volt power supply. This interger value is then converted into a temperature value in celsius.




#I think this class will be a thread created by the refrigerator BaseDeviceRequestHandler, and the
#thermometer itself will post the data to the SQUID.


class TempWatcher(threading.Thread):
    
    def run(self):
        self.is_running == True
        self.SQUID_IP = SQUID_IP
        self.SQUID_PORT = SQUID_PORT
        spi = spidev.SpiDev()
        spi.open(self.spi_port,0)
        print 'spi interface built, tempwatcher is running'
        while self.is_running == True:
            values = spi.xfer2([1,8<<4,0])
            value = ((values[1]&3) << 8) + values[2]
            v = 3.31*value/1024
            x = ((self.R * v)/(3.31 - v))/self.R
            T = 1/(self.A1 + self.B1*math.log(x) + self.C1*math.pow(math.log(x),2) + self.D1*math.pow(math.log(x),3))
            if self.acquire:
                self._post_squid_data({"temperature" : T,"time": datetime.time})
            sleep(10)
            
    def __init__(self, spi_port):
        #Device information and SQUID address
        self.is_running = False
        self.SQUID_IP = ''
        self.SQUID_PORT = ''
        self.uuid = ''
        self.spi_port = spi_port
        #Constants used to calculate temperature
        self.Rref = 10000
        self.R = 25500
        self.A1 = 3.354016e-3
        self.B1 = 2.569850e-4
        self.C1 = 2.620131e-6
        self.D1 = 6.383091e-8
        threading.Thread.__init__(self)
        print 'tempwatcher has been constructed'
    
    
    def _post_squid_data(self,data):
        print 'tempwatcher is posting data to squid'
        d = {"datum[uuid]": self.uuid,
             "datum[data]": data}
        print d
        post_data = urllib.urlencode(d)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        conn = httplib.HTTPConnection(self.SQUID_ID, \
                                      self.SQUID_PORT)
        conn.request("POST",post_data,headers)

    def acquire(self, uuid, ip, port):
        self.uuid = uuid
        self.SQUID_IP = ip
        self.SQUID_PORT = port
        self.acquire = True
        print 'tempwatcher is acquiring data'
