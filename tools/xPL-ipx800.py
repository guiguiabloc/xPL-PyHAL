#! /usr/bin/python
#
# xpl-ipx800
# V.1.0 (16 feb. 2012)
# xPL client for IPX800
# http://www.gce-electronics.com
#
# Copyright (C) 2012  GuiguiAbloc
# http://blog.guiguiabloc.fr
#
# CMD : xpl-sender -m xpl-cmnd -c control.basic device=ipx800 type=output current=on|off data1=1|2|...


import os,socket, select
import threading, time
#################
# CONFIGURATION #
#################
ipx800='192.168.43.8'
m2mport=9870
debug = False

#####################
# END CONFIGURATION #
#####################
buff = 1500

# xPL Common
hostname = socket.gethostname()
ip_addr = socket.gethostbyname_ex(socket.gethostname())[2][0]
source='guigui.ipx800'
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
     msg = "xpl-stat\n{\nhop=1\nsource=" +source+'.' +hostname+"\ntarget=*\n}\nsensor.basic\n{\n" + body + "\n}\n"
     UDPSock.sendto(msg,xpladdr)

def xplmsgtrig(body):
     msg = "xpl-trig\n{\nhop=1\nsource=" +source+'.' +hostname+"\ntarget=*\n}\nsensor.basic\n{\n" + body + "\n}\n"
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
                if self.schema == "control.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            messagestruct = msgLine.partition('=')
                            self.statusDict[messagestruct[0]] = messagestruct[2]
                    try:
                      device = self.statusDict['device']
                    except:
                      print "no device"
                    try:
                      targetrelay = self.statusDict['data1']
                      if debug:
                        print targetrelay
                    except:
                      print "no module defined"
                    try:
                      order = self.statusDict['current']
                      if debug:
                        print order
                    except:
                      print "no current defined"
                    if device == "ipx800" :
                       if targetrelay == "1":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay1(1)
                         if order=="off":
                           relay1(0)
                       if targetrelay == "2":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay2(1)
                         if order=="off":
                           relay2(0)
                       if targetrelay == "3":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay3(1)
                         if order=="off":
                           relay3(0)
                       if targetrelay == "4":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay4(1)
                         if order=="off":
                           relay4(0)
                       if targetrelay == "5":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay5(1)
                         if order=="off":
                           relay5(0)
                       if targetrelay == "6":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay6(1)
                         if order=="off":
                           relay6(0)
                       if targetrelay == "7":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay7(1)
                         if order=="off":
                           relay7(0)
                       if targetrelay == "8":
                         body = 'device='+device+'.'+targetrelay+'\ntype=output\ncurrent='+order
                         xplmsgtrig(body)
                         if order=="on":
                           relay8(1)
                         if order=="off":
                           relay8(0)



            else:
                return None
        else:
            print "No message type"
            return None

# connexion ipx800 M2M
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((ipx800,m2mport))
except Exception, e:
    alert('An error occured with %s:%d. Exception type is %s' % (ipx800addr, m2mport, `e`))

# M2M command
counterstate1 = "GetCount1\r\n"
counterstate2 = "GetCount2\r\n"
relay1off = "Set10\r\n"
relay1on = "Set11\r\n"
relay2off = "Set20\r\n"
relay2on = "Set21\r\n"
relay3off = "Set30\r\n"
relay3on = "Set31\r\n"
relay4off = "Set40\r\n"
relay4on = "Set41\r\n"
relay5off = "Set50\r\n"
relay5on = "Set51\r\n"
relay6off = "Set60\r\n"
relay6on = "Set61\r\n"
relay7off = "Set70\r\n"
relay7on = "Set71\r\n"
relay8off = "Set80\r\n"
relay8on = "Set81\r\n"


def counter1():
    s.send(counter1state)
    data = s.recv(50)
    valeur =data.replace('GetCount=','')
    print valeur
def relay1(value):
    if value==1:
      if debug:
        print relay1on
      s.send(relay1on)
      data = s.recv(50)
    else :
      if debug:
        print relay1off
      s.send(relay1off)
      data = s.recv(50)

def relay2(value):
    if value==1:
      if debug:
        print relay2on
      s.send(relay2on)
      data = s.recv(50)
    else :
      if debug:
        print relay2off
      s.send(relay2off)
      data = s.recv(50)
def relay3(value):
    if value==1:
      if debug:
        print relay3on
      s.send(relay3on)
      data = s.recv(50)
    else :
      if debug:
        print relay3off
      s.send(relay3off)
      data = s.recv(50)

def relay4(value):
    if value==1:
      if debug:
        print relay4on
      s.send(relay4on)
      data = s.recv(50)
    else :
      if debug:
        print relay4off
      s.send(relay4off)
      data = s.recv(50)

def relay5(value):
    if value==1:
      if debug:
        print relay5on
      s.send(relay5on)
      data = s.recv(50)
    else :
      if debug:
        print relay5off
      s.send(relay5off)
      data = s.recv(50)

def relay6(value):
    if value==1:
      if debug:
        print relay6on
      s.send(relay6on)
      data = s.recv(50)
    else :
      if debug:
        print relay6off
      s.send(relay6off)
      data = s.recv(50)

def relay7(value):
    if value==1:
      if debug:
        print relay7on
      s.send(relay7on)
      data = s.recv(50)
    else :
      if debug:
        print relay7off
      s.send(relay7off)
      data = s.recv(50)

def relay8(value):
    if value==1:
      if debug:
        print relay8on
      s.send(relay8on)
      data = s.recv(50)
    else :
      if debug:
        print relay8off
      s.send(relay8off)
      data = s.recv(50)


########
# MAIN #
########

try :
  UDPSock.bind(addr)
except :
  port = 50006
  addr = ("0.0.0.0",port)
  try :
    UDPSock.bind(addr)
  except :
    port += 1
if debug:
  print "xPL ipx800 bound to port " + str(port)
try:
  a = HeartbeatLoop(180, SendHeartBeat())
  a.start()
  while 1==1 :
    readable, writeable, errored = select.select([UDPSock],[],[],60)
    target = "ipx800"
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
          logfile = open('xpl-ipx800.log', 'w')
          logfile.write(data)
          logfile.close()
          print data
    else:
      print "Not connected"
except KeyboardInterrupt:
    print 'Exiting, please wait...'
    a.stop()
    SendEndBeat()

