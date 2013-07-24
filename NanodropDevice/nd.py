from basedevice import BaseDeviceRequestHandler, BaseDevice

import time
import json
import os
import httplib, urllib
from datetime import date

class ndDeviceRequestHandler(BaseDeviceRequestHandler):
  def do_cmd_test(self):
    """ Handle cmd=test
    """
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
        "status"   : "ready",
        "state"    : "",
        "name"     : "Nanodrop"}
    response = json.dumps(info)
    self.wfile.write(response)
      
  def do_cmd_acquire(self):
    self.send_response( 200 )
    self.send_header("content-type", "text/plain")
    self.end_headers()
    self.state["SQUID-IP"] = self.client_address[0];
    self.state["SQUID-PORT"] = self.query["port"];
    self.wfile.write("OK")
      

class ndDevice(BaseDevice):
  def __init__(self,H,settings):
    BaseDevice.__init__(self,H,settings['port'])
    self.settings = settings
    self.datafile = None
  
  def update_time_forever(self):
    while 1:
      self.state["time"] = time.time()
      time.sleep(1)
  
  def _open_data_file(self, data_path):
    """  Checks to see if data_path file is open
    if not, it attempts to open it and seek to the current end.
    if it cannon open the file it returns False
    """
    if (not self.datafile) or \
       (self.datafile.name != data_path) or \
       self.datafile.closed:
      try:
        self.datafile = open(data_path,'r');
        #seek to end of file
        self.datafile.seek(0,os.SEEK_END)
      except IOError:
        #file not found
        return False
    return True
  
  def _post_squid_data(self,path,data):
    d = {"datum[uuid]": self.state["uuid"], \
         "datum[data]": data}
    post_data = urllib.urlencode(d)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    conn = httplib.HTTPConnection(self.state["SQUID-IP"], \
                                  self.state["SQUID-PORT"])
    conn.request("POST",path,post_data,headers)
  
  def monitor_data_file(self):
    while 1:
      data_path = self.settings["datapath"] + \
                  self.settings['datafilename'].format(date.today())
      if self._open_data_file(data_path):
        line = self.datafile.readline()
        if line:
          #TODO: placeholder for adding to DB
          self._post_squid_data("/data",line)
      time.sleep(5)
           

#program entry point
if __name__ == '__main__':
  settings_file = open('settings.JSON') 
  settings = json.load(settings_file)
  settings_file.close()
  dev = ndDevice(ndDeviceRequestHandler,settings)   
   
  dev.start()
  print "serving at port", settings['port']
  dev.monitor_data_file()
