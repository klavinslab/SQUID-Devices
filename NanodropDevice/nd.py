from basedevice import BaseDeviceRequestHandler, BaseDevice

import time
import json

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
   
   def update_time_forever(self):
      while 1:
         self.state["time"] = time.time()
         time.sleep(1)
   

#program entry point
if __name__ == '__main__':
   settings_file = open('settings.JSON') 
   settings = json.load(settings_file)
   settings_file.close()
   dev = ndDevice(ndDeviceRequestHandler,settings)   
    
   dev.start()
   print "serving at port", settings['port']
   dev.update_time_forever()
