# xPLmemcached class for xPL-PyHAL
# Copyright (C) 2012  GuiguiAbloc
# http://blog.guiguiabloc.fr
# http://code.google.com/p/guiguiabloc/

import memcache
import sys, os, time, atexit,  socket

class xplmemcached():
    hostname = ""
    server   = ""
    def __init__(self, hostname="127.0.0.1", port="11211"):
        self.hostname = "%s:%s" % (hostname, port)
        self.server   = memcache.Client([self.hostname])

    def set(self, key, value, expiry=900):
        self.server.set(key, value, expiry)

    def get(self, key):
        return self.server.get(key)

    def delete(self, key):
        self.server.delete(key)

