#! /usr/bin/python
#
# xPL-Notifry
# V.1.1 (28 nov. 2012)
# xPL client for Notifry
# https://notifrier.appspot.com/

# Copyright (C) 2012  GuiguiAbloc
# http://blog.guiguiabloc.fr
#
# CMD : xpl-sender -m xpl-cmnd -c sendmsg.basic to=key@notifry body=bonjour
# CMD : xpl-sender -m xpl-cmnd -c sendmsg.push to=key@notifry title=Hello body=bonjour

import urllib
import urllib2
import sys
import getopt
import json
import os,socket, select
import threading, time
#################
# CONFIGURATION #
#################
BACKEND = 'https://notifrier.appspot.com/notifry';
debug = False

#####################
# END CONFIGURATION #
#####################
buff = 1500

# xPL Common
hostname = socket.gethostname()
ip_addr = socket.gethostbyname_ex(socket.gethostname())[2][0]
source='xPL-Notifry'
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

def xplmsgstat(body):
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+'.' +hostname+"\ntarget=*\n}\nsendmsg.basic\n{\n" + body + "\n}\n"
     UDPSock.sendto(msg,xpladdr)

def xplmsgtrig(body):
     msg = "xpl-trig\n{\nhop=1\nsource=" +source+'.' +hostname+"\ntarget=*\n}\nsendmsg.basic\n{\n" + body + "\n}\n"
     UDPSock.sendto(msg,xpladdr)

def SendHeartBeat ():
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+"." +hostname+ "\ntarget=*\n}\nhbeat.app\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + ip_addr + "\n}\n"
     UDPSock.sendto(msg,("255.255.255.255",3865))

def SendEndBeat ():
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+"." +hostname+ "\ntarget=*\n}\nhbeat.end\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + ip_addr + "\n}\n"
     UDPSock.sendto(msg,("255.255.255.255",3865))

def alert(msg):
    print >>sys.stderr, msg
    sys.exit(1)

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

            if self.fullMessage[0] == 'xpl-cmnd':
                self.type = 'xpl-cmnd'
            else:
                self.type = 'OTHER'

        else:
            print "No treatment"
            return None

    def parseMessage(self):
        if self.type != None:
            if self.type == "xpl-cmnd":
                if self.schema == "sendmsg.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            messagestruct = msgLine.partition('=')
                            self.statusDict[messagestruct[0]] = messagestruct[2]
                    try:
                      totarget = self.statusDict['to']
                      try: 
                            newtarget = totarget.replace("@notifry", "")
                      except:
                        print "No treatment"
                        return None
                    except:
                      print "no device"
                    try:
                      subject = self.statusDict['body']
                      if debug:
                        print subject
                    except:
                      print "no subject defined"

                    params = {}
                    params['format'] = 'json'
                    #requiredCount = 0
                    params['source'] = newtarget
                    params['title'] =  "Alarme"
                    params['message'] = subject
                    try:
                        response = urllib2.urlopen(BACKEND, urllib.urlencode(params))
                        body = response.read()
                        errormessage = 'error'
                        if errormessage in body:
                           print "Server did not accept our message: " + body
                           sys.exit(2)
                        else:
                           print "Message sent OK."

                    except urllib2.URLError, ex:
                        print "Failed to make request to the server: " + str(ex)
                        sys.exit(1)

                if self.schema == "sendmsg.push":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            messagestruct = msgLine.partition('=')
                            self.statusDict[messagestruct[0]] = messagestruct[2]
                    try:
                      totarget = self.statusDict['to']
                      try:
                            newtarget = totarget.replace("@notifry", "")
                      except:
                        print "No treatment"
                        return None
                    except:
                      print "no device"
                    try:
                      subject = self.statusDict['body']
                      if debug:
                        print subject
                    except:
                      print "no subject defined"
                    try:
                      title = self.statusDict['title']
                      if debug:
                        print title
                    except:
                      print "no title defined"

                    params = {}
                    params['format'] = 'json'
                    #requiredCount = 0
                    params['source'] = newtarget
                    params['title'] =  title
                    params['message'] = subject
                    try:
                        response = urllib2.urlopen(BACKEND, urllib.urlencode(params))
                        body = response.read()
                        errormessage = 'error'
                        if errormessage in body:
                           print "Server did not accept our message: " + body
                           sys.exit(2)
                        else:
                           print "Message sent OK."

                    except urllib2.URLError, ex:
                        print "Failed to make request to the server: " + str(ex)
                        sys.exit(1)


            else:
                return None
        else:
            print "No message type"
            return None


########
# MAIN #
########

try :
  UDPSock.bind(addr)
except :
  port = 50007
  addr = ("0.0.0.0",port)
  try :
    UDPSock.bind(addr)
  except :
    port += 1
if debug:
  print "xPL Notifry bound to port " + str(port)
try:
  a = HeartbeatLoop(180, SendHeartBeat())
  a.start()
  while 1==1 :
    readable, writeable, errored = select.select([UDPSock],[],[],60)
    target = "notifry"
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
          print "Parsing XML error"

      xplMsg = xplMessage(messagedata)
      xplMsg.parseMessage()

      if debug:
        if target in data :
          logfile = open('xpl-notifry.log', 'w')
          logfile.write(data)
          logfile.close()
          print data
    else:
      print "Not connected"
except KeyboardInterrupt:
    print 'Exiting, please wait...'
    a.stop()
    SendEndBeat()

