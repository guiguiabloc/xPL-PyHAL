#!/usr/bin/env python
#
# xPL-PyHAL
# v.0.1 (05/2012)
# Copyright (C) 2012  GuiguiAbloc
# http://blog.guiguiabloc.fr
# http://code.google.com/p/guiguiabloc/

import sys, time
import threading
from Daemon import Daemon
from BrainPyHAL import xPLattach
from xPLmessage import xPLmessage

xpl = xPLattach()
message =  xPLmessage()

class HeartbeatLoop:

    def __init__(self, tempo, target):
        self._target = target
        self._tempo = tempo

    def _run(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
        self._target = message.SendHeartBeat()

    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()

class MyDaemon(Daemon):
	def run(self):
          try:
            a = HeartbeatLoop(180, message.SendHeartBeat())
            a.start()
            listener = xpl.startListener(xpl.UDPSock)
            while listener:
              pass
            else:
              print "Could Not Find Listener"
          except KeyboardInterrupt:
            print 'Exiting, please wait...'
            a.stop()
            message.SendEndBeat()

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/daemon-PyHAL.pid')
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
                elif 'console' == sys.argv[1]:
                        daemon.console()

		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart|console" % sys.argv[0]
		sys.exit(2)
