#!/usr/bin/env python
import logging
import logging.config
import sys
import os

import yaml
import tornado.ioloop
import tornado.web

import store
import handler


logging.config.dictConfig(
    yaml.load(open('logging.yaml', 'r')))


application = tornado.web.Application([
    (r'/(?P<format>[^\/]+)/(?P<ip>[\d\.]+)', handler.IPQueryHandler),
    (r'/(?P<format>[^\/]+)/batch', handler.IPBatchQueryHandler),
])


def to_abs_path(path):
    if path.startswith('.'):
        path = os.path.join(os.getcwd(), path)

    return path


if __name__ == "__main__":
    application.listen(
        int(sys.argv[1]))
    logging.info('app would be listen on: %s' % sys.argv[1])
    path = to_abs_path(sys.argv[2])
    logging.info('about to load ip db: %s' % path)
    ip_store = store.InMemStore.load(path)
    logging.info('finish loading ip db.')
    application.ip_store = ip_store
    tornado.ioloop.IOLoop.instance().start()
