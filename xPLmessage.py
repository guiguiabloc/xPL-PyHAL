# xPLmessage class for xPL-PyHAL
# Copyright (C) 2013  GuiguiAbloc
# http://blog.guiguiabloc.fr
# http://code.google.com/p/guiguiabloc/

import socket
import os

UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
UDPSock.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)


class xPLmessage:
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname_ex(socket.gethostname())[2][0]
    source='HAL'
    xpl_port = 3865
    xplschema = 'notdefined'
    def __init__(self):
        self.body = None
    def xplmsgstat(body):
        msg = "xpl-stat\n{\nhop=1\nsource=" +source +hostname+"\ntarget=*\n}\n"+xplschema+"\n{\n" + body + "\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgtrig(self,body):
        msg = "xpl-trig\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\n"+xPLmessage.xplschema+"\n{\n" + body + "\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgnotifry(self,keynotifry,body):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nsendmsg.basic\n{\nto=" +keynotifry+"@notifry\nbody=" + body + "\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgsms(self,phone,body):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nsendmsg.basic\n{\nto=" +phone+"\nbody=" + body + "\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgnotifryfull(self,keynotifry,titlenotifry,body):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nsendmsg.push\n{\nto=" +keynotifry+"@notifry\ntitle=" + titlenotifry +"\nbody=" + body + "\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgcmndx10(self,commandx10,devicex10):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nx10.basic\n{\ncommand="+ commandx10+"\ndevice="+devicex10+"\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgcmndchacon(self,addresschacon,unitchacon,commandchacon):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nhomeeasy.basic\n{\naddress="+addresschacon+"\nunit="+ unitchacon+"\ncommand="+commandchacon+"\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgcmndchaconpreset(self,addresschacon,unitchacon,levelchacon):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\nhomeeasy.basic\n{\naddress="+addresschacon+"\nunit="+ unitchacon+"\ncommand=preset\nlevel="+levelchacon+"\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)

    def xplmsgcmndipx800(self,commandipx800,relayipx800):
        msg = "xpl-cmnd\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+"\ntarget=*\n}\ncontrol.basic\n{\ndevice=ipx800\ncurrent="+ str(commandipx800)+"\ndata1="+str(relayipx800)+"\n}\n"
        xpladdr = ("255.255.255.255",3865)
        xplport = 3865
        UDPSock.sendto(msg,xpladdr)


    def SendHeartBeat (self, port=50002):
        msg = "xpl-stat\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+ "\ntarget=*\n}\nhbeat.app\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + xPLmessage.ip_addr + "\n}\n"
        UDPSock.sendto(msg,("255.255.255.255",3865))

    def SendEndBeat (self, port=50002):
        msg = "xpl-stat\n{\nhop=1\nsource=" +xPLmessage.source+"." +xPLmessage.hostname+ "\ntarget=*\n}\nhbeat.end\n{\ninterval=5\nport=" + str(port) + "\nremote-ip=" + xPLmessage.ip_addr + "\n}\n"
        UDPSock.sendto(msg,("255.255.255.255",3865))

