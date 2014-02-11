#! /usr/bin/python
#
# xpl-cityzendata
# V.0.1 (08 feb. 2014)
# xPL client for CityzenData
#
# Copyright (C) 2014  GuiguiAbloc
# http://blog.guiguiabloc.fr
#

import urllib
import urllib2
import sys
import os,socket, select
import threading, time
import ConfigParser

#################
# CONFIGURATION #
#################
token = 'your_writeToken'
url =  'http://url_endpoint'
headers = { 'X-CityzenData-Token' : token }

debug = False

#####################
# END CONFIGURATION #
#####################
buff = 1500
parser = ConfigParser.RawConfigParser()


# xPL Common
hostname = socket.gethostname()
ip_addr = socket.gethostbyname_ex(socket.gethostname())[2][0]
source='xPL-CityzenData'
xplschema = 'notdefined'
xpladdr = ("255.255.255.255",3865)
xplport = 3865
UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
UDPSock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)

class HeartbeatLoop:

    def __init__(self, tempo, target):
        self._target = target
        self._tempo = tempo
    def _run(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
        self._target = SendHeartBeat()
    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
    def stop(self):
        self._timer.cancel()

def SendHeartBeat ():
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+"." +hostname+ "\ntarget=*\n}\nhbeat.app\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + ip_addr + "\n}\n"
     UDPSock.sendto(msg,(xpladdr))

def SendEndBeat ():
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+"." +hostname+ "\ntarget=*\n}\nhbeat.end\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + ip_addr + "\n}\n"
     UDPSock.sendto(msg,(xpladdr))

def alert(msg):
    print >>sys.stderr, msg
    sys.exit(1)

def cityzenposttemp(name,valuetemp):
   senddata = "{room=" +name+"} " +valuetemp
   value= '// temperature'
   data = value+senddata
   req = urllib2.Request(url,data,headers)
   try:
     response = urllib2.urlopen(req)
   except URLError,e:
     print "no response from API"
     print e.reason
   if debug:
     print response.info()
     print response.getcode()

def cityzenposthumidity(name,valuehumidity):
   senddata = "{room=" +name+"} " +valuehumidity
   value= '// humidity'
   data = value+senddata
   req = urllib2.Request(url,data,headers)
   try:
     response = urllib2.urlopen(req)
   except URLError,e:
     print "no response from API"
     print e.reason
   if debug:
     print response.info()
     print response.getcode()

def cityzenpostenergy(name,valueenergy):
   senddata = "{room=" +name+"} " +valueenergy
   value= '// energy'
   data = value+senddata
   req = urllib2.Request(url,data,headers)
   try:
     response = urllib2.urlopen(req)
   except URLError,e:
     print "no response from API"
     print e.reason
   if debug:
     print response.info()
     print response.getcode()


# Messages parsing

class xplMessage:
    fullMessage = None
    schema = None
    type = None
    unit =  None
    statusDict = {}

    def __init__(self, messagedata = None):
        if messagedata != None:
            self.fullMessage = messagedata
            self.schema = self.fullMessage[4]

            if self.fullMessage[0] == 'xpl-trig':
                self.type = 'xpl-trig'
            else:
                self.type = 'OTHER'

        else:
            print "No treatment"
            return None

    def parseMessage(self):
        if self.type != None:
            if self.type == "xpl-trig":
                if self.schema == "sensor.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            messagestruct = msgLine.partition('=')
                            self.statusDict[messagestruct[0]] = messagestruct[2]
                    try:
                      sonde = self.statusDict['device']
                      parser.read("config.sonde")
                      checksonde = parser.items("SONDES")
                      if sonde in str(checksonde):
                        nomsonde = parser.get('SONDES', sonde)
                        valuetype = self.statusDict['type']
                        if valuetype == "temp":
                          valuetemp = self.statusDict['current']
                          cityzenposttemp(nomsonde,valuetemp)
                        if valuetype == "humidity":
                          valuehumidity = self.statusDict['current']
                          cityzenposthumidity(nomsonde,valuehumidity)
                        if valuetype == "energy":
                          valueenergy = self.statusDict['current']
                          cityzenpostenergy(nomsonde,valueenergy)

                    except:
                      print "no message"

            else:
                return None
        else:
            print "No message type"
            return None


########
# MAIN #
########
port = 50009

while 1==1 :

  try :
    addr = ("0.0.0.0",port)
    UDPSock.bind(addr)
    break
  except :
    port +=1
    if debug:
      print "port already in use"
if debug:
  print "xPL CityzenData bound to port " + str(port)

try:
  a = HeartbeatLoop(180, SendHeartBeat())
  a.start()
  while 1==1 :
    readable, writeable, errored = select.select([UDPSock],[],[],60)
    target = "sensor.basic"
    if len(readable) == 1 :
      data,addr = UDPSock.recvfrom(buff)
      messagedata = data.splitlines()
      try:
        for msgLine in messagedata:
          if msgLine == '{':
             messagedata.remove(msgLine)
          elif msgLine == '}':
             messagedata.remove(msgLine)
      except:
          print "Parsing error"

      xplMsg = xplMessage(messagedata)
      xplMsg.parseMessage()

      if debug:
        if target in data :
          logfile = open('xpl-cityzendata.log', 'w')
          logfile.write(data)
          logfile.close()
          print data
    else:
      print "No messages"
except KeyboardInterrupt:
    print 'Exiting, please wait...'
    a.stop()
    SendEndBeat()

