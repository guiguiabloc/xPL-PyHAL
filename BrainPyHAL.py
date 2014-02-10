# xPL-PyHAL
# Brain class
# v.0.5 (03/2013)
# Copyright (C) 2013  GuiguiAbloc
# http://blog.guiguiabloc.fr
# http://code.google.com/p/guiguiabloc/

from socket import *
import re,select,sys,time,os,glob
import yaml,datetime
#import hashlib
from xPLmessage import xPLmessage
from PushingBox import pushingbox
try:
  from Memcached_pylibmc import xplmemcached
except:
  from Memcached import xplmemcached

hour = time.strftime('[%Y-%b-%d %H:%M:%S]  ') 
#hour2stamp = time.strftime('%Y-%m-%d %H:%M:%S') 
#timestamper = int(datetime.datetime.strptime(hour2stamp, '%Y-%m-%d %H:%M:%S').strftime("%s"))

# Debug : set True or False
debug = False

class xPLattach:
    message_buffer = 1500
    xpl_port = 50002
    ip_addr = gethostbyname_ex(gethostname())[2][0]
    hostname = gethostname()
    UDPSock = socket(AF_INET,SOCK_DGRAM)
    addr = ("0.0.0.0",xpl_port)
  
    def __init__(self):
        if self.ip_addr == "127.0.0.1":
          print " --------------------------------------------------------"
          print "Error, cannot resolve server hostname ! (return 127.0.0.1)"
          print "please define lan IP and hostname in /etc/hosts"
          print "like : 192.168.1.1 server"
          print " --------------------------------------------------------"
          sys.exit(1)
        else:
          pass

        try :
            self.UDPSock.bind(self.addr)
        except :
            self.xpl_port = 50000
            self.addr = (self.ip_addr, self.xpl_port)
  
            try :
                self.UDPSock.bind(self.addr)
            except :
                self.xpl_port += 1
        if debug : 
          print bcolors.GREEN + hour + "xPL-PyHAL bound to port: " + str(self.xpl_port) + bcolors.ENDC
          print bcolors.RED + self.ip_addr + bcolors.ENDC

  
    def startListener (self, UDPSock = None):
  
        while UDPSock :
            readable, writeable, errored = select.select([UDPSock],[],[],60)
  
            if len(readable) == 1 :
                data,addr = UDPSock.recvfrom(self.message_buffer)
                messageArray = data.splitlines()
                #hour2stamp = time.strftime('%Y-%m-%d %H:%M:%S')
                #timestamper = int(datetime.datetime.strptime(hour2stamp, '%Y-%m-%d %H:%M:%S').strftime("%s"))
                logbegin = "\n XPL MESSAGE:\n"
                logend = "\nEND XPL MESSAGE\n\n"
  
                try:
                    for msgLine in messageArray:
                        if msgLine == '{':
                            messageArray.remove(msgLine)
                        elif msgLine == '}':
                            messageArray.remove(msgLine)
                except:
                    print "Error in parsing xpl message"
  
                if debug:
                  xplmsglog = open("logxplhal.log", "a")
                  xplmsglog.write(logbegin)
                  xplmsglog.write(str(messageArray))
                  xplmsglog.write(logend)
                  xplmsglog.close()
  
                xplMsg = xplMessage(messageArray)
                xplMsg.parseMessage()
  
                if xplMsg.type == "xpl-trig":
                  if debug:
                    try:
                      print xplMsg.statusDict['status']
                    except:
                      print "no daynight"
                    try:
                      print xplMsg.statusDict['device']
                    except:
                      print "unknown device"
  
class xplMessage:
    fullMessage = None
    schema = None
    type = None
    unit =  None
    status =  None
    statusDict = {}
    def __init__(self, messageArray = None):
        if messageArray != None:
            self.fullMessage = messageArray
            self.schema = self.fullMessage[4]
             
            if self.fullMessage[0] == 'xpl-trig':
                self.type = 'xpl-trig'
            elif self.fullMessage[0] == 'xpl-stat':
                self.type = 'xpl-stat'
            elif self.fullMessage[0] == 'xpl-cmnd':
                self.type = 'xpl-cmnd'
            else:
                self.type = 'OTHER'
  
        else:
            print "Error in message array"
            return None


 
    def parseMessage(self):
        # Yaml functions 
        # ACTION script
        def actionscript():
          if yamlload['ACTION'] == "script" :
            try:
              scripttorun = yamlload['SCRIPTNAME']
            except:
              return
            try:
              if self.schema == "dawndusk.basic" or self.schema == "x10.security" or self.schema == "cid.basic" :
                os.system(scripttorun)
                if debug:
                  print bcolors.GREEN + hour + "EXECUTE  : "+scripttorun+ bcolors.ENDC
              else:
                if self.schema == "sensor.basic":
                  commandxpl =  self.statusDict['current']
                else:
                  commandxpl =  self.statusDict['command']
            except:
              if debug:
                print bcolors.RED + hour + "TARGET : error no commmand "
                return
            try:
              commandtocheck = yamlload['COMMAND']
            except:
              return
            if commandtocheck == commandxpl:
              os.system(scripttorun)
              if debug:
                print bcolors.GREEN + hour + "EXECUTE  : "+scripttorun+ bcolors.ENDC

        # ACTION log
        def actionlog():
          if yamlload['ACTION'] == "log" :
            print "match action log"
            try:
              logfilename =  yamlload['TARGETXPL']
            except:
              return
            FILELOG = open(logfilename,"a")
            try:
              MSGLOG= hour + yamlload['MESSAGE'] + "\n"
            except:
              MSGLOG = hour + str(devicetoact) + "\n"
              FILELOG.writelines(MSGLOG)
              FILELOG.close()
              if debug:
                 print bcolors.GREEN + hour + "LOG TO : "+str(logfilename)+ bcolors.ENDC

        # ACTION store memcached
        def actionstorememcached():
          if yamlload['ACTION'] == "store" :
            if debug:  
               print "match action store"
            if yamlload['TARGETXPL'] == "memcached":
               if self.schema == "homeeasy.basic" or self.schema == "ac.basic": 
                 if yamlload['UNIT'] == unittoact :
                   pass
                 else:
                   if debug:
                     print "homeeasy.basic not contain unit"
                   return
               try:
                 commandxpl =  yamlload['VALUE']
               except:
                 try:
                   if self.schema == "dawndusk.basic" :
                     commandxpl = self.statusDict['status']
                   else:
                     if self.schema == "sensor.basic":
                       commandxpl = self.statusDict['current']
                     else:
                       commandxpl = self.statusDict['command']
                 except:
                   if debug:
                     print bcolors.RED + hour + "MEMCACHED : error no value "
                   return 
               try:
                 keymem = yamlload['KEY']
               except:
                 if debug:
                   print bcolors.RED + hour + "MEMCACHED : error no key "
                 return
               try:
                 timekey = int(yamlload['TIME'])
               except:
                 timekey = 0
               loadmem = xplmemcached();
               loadmem.set(keymem, commandxpl,timekey);
               if debug:
                 print bcolors.GREEN + hour + "MEMCACHED : "+str(keymem)+str(commandxpl)+str(timekey)+ bcolors.ENDC

        # ACTION message
        def actionmessage():
          if yamlload['ACTION'] == "message" :
             if yamlload['TARGETXPL'] == "pushingbox":
                try :
                  key = yamlload['KEY']
                except:
                  if debug:
                    print bcolors.RED + hour + "PUSHINGBOX : error no key "
                    return
                pushingbox(key)
                if debug:
                   print bcolors.GREEN + hour + "Send message to PushingBox" + bcolors.ENDC
             if yamlload['TARGETXPL'] == "notifry":
                try:
                  keynotifry = yamlload['KEY']
                except:
                  if debug:
                    print bcolors.RED + hour + "NOTIFRY : error no key "
                  return
                try:
                  messagenotifry = yamlload['MESSAGE']
                except:
                  messagenotifry = None
                try:
                  titlenotifry = yamlload['TITLE']
                except:
                  titlenotifry = None
                commandtocheck = None
                if messagenotifry is None :
                   if self.schema == "cid.basic" :
                     body = "Asterisk Call : " + commandtodo
                   else:
                     try:
                       body = addresstoact + " " + commandtodo
                     except:
                       body = devicetoact + " " + commandtodo
                   time.sleep(10)
                   sendmsg.xplmsgnotifry(keynotifry,body)
                else :
                    if titlenotifry is not None:
                      if self.schema == "dawndusk.basic" or self.schema == "x10.security" :
                        commandxpl = "FORCED"
                      else:
                        if self.schema == "sensor.basic":
                          commandxpl =  self.statusDict['current']
                        else:
                          commandxpl =  self.statusDict['command']
                        try:
                          commandtocheck = yamlload['COMMAND']
                        except:
                          return
                      if commandtocheck == commandxpl or commandxpl == "FORCED":
                        body = messagenotifry
                        time.sleep(10)
                        sendmsg.xplmsgnotifryfull(keynotifry,titlenotifry,body)
                        if debug:
                          print bcolors.GREEN + hour + "Send message to Notifry" + bcolors.ENDC
                    else:
                      if self.schema == "dawndusk.basic" or self.schema == "x10.security" :
                        commandxpl = "FORCED"
                      else:
                        commandxpl =  self.statusDict['command']
                        try:
                          commandtocheck = yamlload['COMMAND']
                        except:
                          return
                      if commandtocheck == commandxpl or commandxpl == "FORCED":
                        body = messagenotifry
                        time.sleep(10)
                        sendmsg.xplmsgnotifry(keynotifry,body)
                        if debug:
                          print bcolors.GREEN + hour + "Send message to Notifry" + bcolors.ENDC

             if yamlload['TARGETXPL'] == "sms":
               try:
                 phone = yamlload['PHONE']
               except:
                 if debug:
                   print bcolors.RED + hour + "SMS : error no phone number "
                 return
               try:
                 messagesms = yamlload['MESSAGE']
               except:
                 if debug:
                   print bcolors.RED + hour + "SMS : error no message "
                 return
               commandtocheck = None
               if self.schema == "dawndusk.basic" or self.schema == "x10.security" :
                 commandxpl = "FORCED"
               else:
                 commandxpl =  self.statusDict['command']
                 try:
                   commandtocheck = yamlload['COMMAND']
                 except:
                   return
               if commandtocheck == commandxpl or commandxpl == "FORCED":
                 body = messagesms
                 time.sleep(10)
                 sendmsg.xplmsgsms(phone,body)
                 if debug:
                   print bcolors.GREEN + hour + "Send message to SMS" + bcolors.ENDC

  

        # ACTION command 
        def actioncommand():
          if yamlload['ACTION'] == "command" :
             if debug:
               print "match action command"
             if self.schema == "homeeasy.basic" or self.schema == "ac.basic":
                if yamlload['UNIT'] == unittoact :
                   pass
                else:
                   if debug:
                     print "YAML not contain unit"
                   return

             if yamlload['TARGETXPL'] == "heyu":
                   if yamlload['TARGETMODULE'] is not None:
                      try:
                        if self.schema == "dawndusk.basic" or self.schema == "x10.security" or self.schema == "cid.basic" :
                          try:
                            commandx10 = yamlload['TARGETCOMMAND']
                          except:
                            if debug:
                              print "no target command in YAML"
                            return
                        else:
                          if self.schema == "sensor.basic":
                            commandx10 =  self.statusDict['current']
                          else:
                            commandx10 =  self.statusDict['command']
                      except:
                        if debug:
                          print bcolors.RED + hour + "TARGET : error no commmand "
                        return

                      devicex10 = yamlload['TARGETMODULE']
                      sendmsg.xplmsgcmndx10(commandx10,devicex10)
                      if debug:
                        print bcolors.GREEN + hour + "Send HEYU Command" + bcolors.ENDC
             if yamlload['TARGETXPL'] == "ipx800":
                   if yamlload['TARGETMODULE'] is not None:
                      try:
                        if self.schema == "dawndusk.basic" or self.schema == "x10.security" or self.schema == "cid.basic" :

                          try:
                            commandipx800 = yamlload['TARGETCOMMAND']
                          except:
                            if debug:
                              print "no target command in YAML"
                            return
                        else:
                          commandipx800 =  self.statusDict['command']
                           
                      except:
                        if debug:
                          print bcolors.RED + hour + "TARGET : error no commmand "
                        return 
                      relayipx800 = yamlload['TARGETMODULE']
                      sendmsg.xplmsgcmndipx800(commandipx800,relayipx800)
                      if debug:
                        print bcolors.GREEN + hour + "Send IPX800 Command" + bcolors.ENDC

        if self.type != None:
            hour = time.strftime('[%Y-%b-%d %H:%M:%S]  ')
            if self.type == "xpl-trig":
                # SCHEMA sensor.basic
                if self.schema == "sensor.basic":
                  if debug:
                    print bcolors.GREY + hour + "Ignoring sensor.basic Message" + bcolors.ENDC
                  for msgLine in self.fullMessage:
                    if msgLine.find('=') != -1:
                      GlobalArray = msgLine.partition('=')
                      self.statusDict[GlobalArray[0]] = GlobalArray[2]
                    try:
                      verifydevice = self.statusDict['device']
                      if verifydevice == "ipx800":
                        devicetoact = self.statusDict['data1']
                        commandtodo = self.statusDict['current']
                        sendmsg = xPLmessage()
                        yamldir = "./yamlrepo/"
                        for root, dirs, files in os.walk(yamldir):
                          for file in files:
                            if file.endswith(".yaml"):
                               yamlload = yaml.load(open(yamldir+file))
                               if devicetoact == yamlload['MODULE']:
                                 actionstorememcached()
                                 actionmessage()
                                 actioncommand()
                                 actionlog()
                                 actionscript()

                    except:
                      pass
                  return  None
                # SCHEMA x10.security
                if self.schema == "x10.security":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]
                    try:
                      testtamper = self.statusDict['tamper']
                      if testtamper:
                        return
                    except:
                      if debug:
                        print "ALARME x10 SECURITY"
                      devicetoact = self.statusDict['device']
                      commandtodo = self.statusDict['command']
                      #load yaml
                      sendmsg = xPLmessage()
                      yamldir = "./yamlrepo/"
                      for root, dirs, files in os.walk(yamldir):
                        for file in files:
                          if file.endswith(".yaml"):
                             yamlload = yaml.load(open(yamldir+file))
                             if devicetoact == yamlload['MODULE']:
                               actioncommand()
                               actionmessage()
                               actionlog()          
                               actionscript()
                               actionstorememcached()

                # SCHEMA x10.basic
                elif self.schema == "x10.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]

                    commandtodo = self.statusDict['command']
                    devicetoact = self.statusDict['device']
                    #load yaml
                    sendmsg = xPLmessage()
                    yamldir = "./yamlrepo/"
                    for root, dirs, files in os.walk(yamldir):
                        for file in files:
                          if file.endswith(".yaml"):
                             yamlload = yaml.load(open(yamldir+file))
                             try:
                                devicetoact == yamlload['MODULE']
                             except:
                                return
                             if devicetoact == yamlload['MODULE']:
                                 if debug:
                                   print "MATCH !"+ yamlload['MODULE'] + "Must do "+ yamlload['ACTION']

                                 actioncommand()
                                 actionmessage()            
                                 actionstorememcached()
                                 actionscript()
                                 actionlog()            

                                           
                # SCHEMA homeeasy.basic
                elif self.schema == "homeeasy.basic" or self.schema == "ac.basic":
                    # futur
                    #hour2stamp = time.strftime('%Y-%m-%d %H:%M:%S')
                    #timestamper = int(datetime.datetime.strptime(hour2stamp, '%Y-%m-%d %H:%M:%S').strftime("%s"))
                    #sMd5SumAddress = hashlib.md5(self.fullMessage[5]).hexdigest()
                    #sMd5SumUnit = hashlib.md5(self.fullMessage[6]).hexdigest()
                    #sMd5Module = sMd5SumAddress+sMd5SumUnit
                    #ts1 = timestamper+1
                    #ts2 = timestamper+2
                    #ts3 = timestamper+3
                    #ts4 = timestamper+4
                    #loadmem = xplmemcached();
                    #OKModule = sMd5Module+str(timestamper)
                    #WModule1 = sMd5Module+str(ts1)
                    #WModule2 = sMd5Module+str(ts2)
                    #WModule3 = sMd5Module+str(ts3)
                    #verifyMCOKModule = loadmem.get(OKModule)
                    #verifyMCWModule1 = loadmem.get(WModule1)
                    #verifyMCWModule2 = loadmem.get(WModule2)
                    #verifyMCWModule3 = loadmem.get(WModule3)
                    #if verifyMCOKModule or verifyMCWModule1 or verifyMCWModule2 or verifyMCWModule3 :
                      #if debug:
                      # print "always seen this module"
                      #return
                    #else:
                      #if debug:
                        #print "ok for analyse"  
                        #print "MODULE : "+str(OKModule)
                      #loadmem.set(OKModule, "ok",5);
                      #loadmem.set(WModule1, "ok",5);
                      #loadmem.set(WModule2, "ok",5);
                      #loadmem.set(WModule3, "ok",5);
                    #if debug:
                      #print "Adresse : "+self.fullMessage[5]
                      #print "Somme MD5 : "+sMd5SumAddress
                      #print "Unite : "+self.fullMessage[6]
                      #print "Somme MD5 : "+sMd5SumUnit
                      #print sMd5Module
                      #print "TimeStamp : "+str(timestamper)
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]

                    commandtodo = self.statusDict['command']
                    addresstoact = self.statusDict['address']
                    unittoact = self.statusDict['unit']
                    #load yaml
                    sendmsg = xPLmessage()
                    yamldir = "./yamlrepo/"
                    for root, dirs, files in os.walk(yamldir):
                        for file in files:
                          if file.endswith(".yaml"):
                             yamlload = yaml.load(open(yamldir+file))
                             try: 
                               addresstoact == yamlload['MODULE']
                             except:
                               return
                             if addresstoact == yamlload['MODULE']:
                               if yamlload['UNIT'] :
                                  unittoact == yamlload['UNIT']
                                  if debug:
                                    print "MATCH !"+ yamlload['MODULE'] + " and  unit " +unittoact+" Must do "+ yamlload['ACTION']

                                  actioncommand()
                                  actionmessage()
                                  actionscript()
                                  actionlog()
                                  actionstorememcached() 

                # SCHEMA dawndusk.basic
                elif self.schema == "dawndusk.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]
                    commandtodo = self.statusDict['status']
                    devicetoact = self.statusDict['type']
                    daynightstatustoact = None
                    sendmsg = xPLmessage()
                    yamldir = "./yamlrepo/"
                    for root, dirs, files in os.walk(yamldir):
                        for file in files:
                          if file.endswith(".yaml"):
                             yamlload = yaml.load(open(yamldir+file))
                             if devicetoact == yamlload['MODULE']:
                               try:
                                 daynightstatustoact = yamlload['DAYNIGHT']
                               except:
                                 return
                               if daynightstatustoact == commandtodo:
                                  actioncommand()
                                  actionmessage()
                                  actionscript()
                                  actionlog()
                                  actionstorememcached()


                # SCHEMA cid.basic
                elif self.schema == "cid.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]
                    commandtodo = self.statusDict['phone'] 
                    devicetoact = self.statusDict['calltype']
                    numbertoact = None
                    sendmsg = xPLmessage()
                    yamldir = "./yamlrepo/"
                    for root, dirs, files in os.walk(yamldir):
                        for file in files:
                          if file.endswith(".yaml"):
                             yamlload = yaml.load(open(yamldir+file))
                             if devicetoact == yamlload['MODULE']:
                               if debug:
                                 print "match cid.basic"
                               try:
                                 numbertoact = yamlload['TELNUMBER']
                               except:
                                 actionmessage()
                                 return
                               if numbertoact == commandtodo:
                                  actioncommand()
                                  actionmessage()
                                  actionscript()
                                  actionlog()
                                  actionstorememcached()

                # fin
                else:
                    if debug:
                      print bcolors.RED + hour + "Unknown xpl-trig schema. Not implemented" + bcolors.ENDC
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]

                    return None




            elif self.type == "xpl-stat":
              if debug:
                print bcolors.GREY + hour + "Ignoring xpl-stat Message" + bcolors.ENDC
            elif self.type == "xpl-cmnd":
               # SCHEMA CONTROL.BASIC
                if self.schema == "control.basic":
                    for msgLine in self.fullMessage:
                        if msgLine.find('=') != -1:
                            GlobalArray = msgLine.partition('=')
                            self.statusDict[GlobalArray[0]] = GlobalArray[2]
                    commandtodo = self.statusDict['current']
                    devicetoact = self.statusDict['device']
                    if debug:
                      print commandtodo
                      print devicetoact
                if debug:
                  print bcolors.GREY + hour + "xpl-cmnd Message" + bcolors.ENDC
            else:
                if debug:
                  print bcolors.CYAN + hour + "Unknown Message Type" + bcolors.ENDC
                return None
        else:
            if debug:
              print "Your instance must have a message type"
            return None

class bcolors:
    OKBLUE = '\033[94m'
    GREEN = '\033[1;92m'
    WARNING = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    GREY="\033[1;30m"
    LIGHT_GREY="\033[0;37m"
    CYAN="\033[0;36m"
    LIGHT_CYAN="\033[1;36m\]"

    def disable(self):
        self.OKBLUE = ''
        self.GREY = ''
        self.LIGHT_GREY = ''
        self.GREEN = ''
        self.RED = ''
        self.WARNING = ''
        self.ENDC = ''

