#!/usr/bin/env python
import tornado.ioloop
import tornado.web

try:
    import ujson as json
except:
    import json


class IPQueryHandler(tornado.web.RequestHandler):

    header_mapping = {
        'jsonp': ("Content-Type", "text/javascript; charset=UTF-8"),
        'json': ("Content-Type", "application/json"),
    }

    def get(self, format, ip):
        header = self.header_mapping.get(format)
        self.set_header(*header)
        ip_store = self.application.ip_store
        info = ip_store.find_location_by_ip(ip)
        json_ret = json.dumps(info)

        if format == 'json':
            ret = json_ret
        elif format == 'jsonp':
            cb = self.get_argument('callback')
            ret = '{}({});'.format(cb, json_ret)

        self.write(ret)


class IPBatchQueryHandler(tornado.web.RequestHandler):

    header_mapping = {
        'jsonp': ("Content-Type", "text/javascript; charset=UTF-8"),
        'json': ("Content-Type", "application/json"),
    }

    def batch_getip(self, format):
        header = self.header_mapping.get(format)
        self.set_header(*header)

        ret = {}
        ips = set(self.get_argument('ip', '').split(','))
        for ip in ips:
            if ip:
                ret[ip] = self.application.ip_store.find_location_by_ip(ip)

        json_ret = json.dumps(ret)

        if format == 'json':
            self.write(json_ret)
        elif format == 'jsonp':
            cb = self.get_argument('callback')
            self.write(cb)
            self.write('(')
            self.write(json_ret)
            self.write(');')

    def post(self, format):
        self.batch_getip(format)

    def get(self, format):
        self.batch_getip(format)
