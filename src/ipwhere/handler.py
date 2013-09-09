#!/usr/bin/env python
import tornado.ioloop
import tornado.web
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
