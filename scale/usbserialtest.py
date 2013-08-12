#!/usr/bin/env python
import serial as pyserial
from threading import Thread
import datetime
import math
import time

current_value = 0
tolerance = 0.01

class scaleReader(Thread):
    def run(self):
        while self.is_running:
            line = self.serial.readline()
            if len(line) > 3:
                self.parse_data(line)
                #print line
    def __init__(self, device, baud):
        Thread.__init__(self)
        self.serial = pyserial.Serial(port=device,baudrate=baud)
        self.is_running = False
    
    def start(self):
        self.is_running = True
        Thread.start(self)
        
    """Parses data from scale"""
    def parse_data(self, line):
        global current_value
        global tolerance
        code = line[0:2]
        sign = line [5]
        value = line[9:-5]
        if code == 'ST':
            if math.fabs(float(value) - current_value) > tolerance:
                current_value = float(value)
                if sign == '+':
                    print current_value
                    print time.time()
                elif sign == '=':
                    current_value = -current_value
                    print current_value
                    print time.time()
if __name__ == '__main__':
    dev = scaleReader('/dev/ttyUSB0',9600)
    dev.start()
    raw_input ('Press anything to stop this madness!')
    dev.is_running = False 