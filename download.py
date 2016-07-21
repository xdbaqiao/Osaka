#!/usr/bin/python2
# coding:utf8

import time
import urllib2
import socket

class download:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:5.0) Gecko/20100101 Firefox/5.0'
        self.headers = {'User-Agent': self.user_agent, 'Accept-encoding':'gzip, deflate'}
        self.opener = urllib2.build_opener()
        socket.setdefaulttimeout(20)

    def get(self, url):
        print '%s Downloading: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), url)
        request = urllib2.Request(url)
        response = self.opener.open(request)
        html = response.read()
        return html
