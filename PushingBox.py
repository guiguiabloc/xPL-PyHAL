# xPL-Pushingbox class for xPL-PyHAL
# Copyright (C) 2012  GuiguiAbloc
# http://blog.guiguiabloc.fr
# http://code.google.com/p/guiguiabloc/

import urllib, urllib2

class pushingbox():
    url = ""
    def __init__(self, key):
        url = 'http://api.pushingbox.com/pushingbox'
        values = {'devid' : key}
        try:
          data = urllib.urlencode(values)
          req = urllib2.Request(url, data)
          sendrequest = urllib2.urlopen(req)
        except Exception, detail:
          print "Error ", detail

