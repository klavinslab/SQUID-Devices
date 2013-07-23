from basedevice import BaseDeviceRequestHandler, BaseDevice

import time
import json

class TestDeviceRequestHandler(BaseDeviceRequestHandler):
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
          "name"     : "Example Device"}
      response = json.dumps(info)
      self.wfile.write(response)
      
   def do_cmd_acquire(self):
      self.state["SQUID-IP"] = self.client_address[0];
      self.state["SQUID-PORT"] = self.query["port"];
      pass

class TestDevice(BaseDevice):
   def update_time_forever(self):
      while 1:
         self.state["time"] = time.time()
         time.sleep(1)
   

#program entry point
if __name__ == '__main__':
   PORT = 8000
   dev = TestDevice(TestDeviceRequestHandler,PORT)   
    
   dev.start()
   print "serving at port", PORT
   dev.update_time_forever()
