from fabric.api import task
import redis
import sqlite3
import os
import store
import utils
import bson
from pympler import summary
from pympler import muppy
import timeit


redis_srv = redis.StrictRedis(host='localhost', port=6379, db=0)


def provision_city_location(cursor):
    columns = [
        'loc_id',
        'country_code',
        'region_code',
        'city_name',
        'postal_code',
        'latitude',
        'longitude',
        'metro_code',
        'area_code',
    ]

    for row in cursor.execute("SELECT * from city_location order by loc_id ASC"):
        d = {}
        d = dict((col, row[idx]) for (idx, col) in enumerate(columns))
        redis_srv.rpush('loc:{}'.format(d['loc_id']), *row)


def provision_ipstart_index(cursor):
    columns = [
        'ip_start',
        'ip_end',
        'loc_id'
    ]

    for row in cursor.execute("SELECT * from city_blocks order by loc_id ASC"):
        d = {}
        d = dict((col, row[idx]) for (idx, col) in enumerate(columns))
        pkey_idx = redis_srv.llen('location_list')
        redis_srv.zadd('ip_start_idx', int(d['ip_start']), int(pkey_idx))
        redis_srv.rpush('location_list', int(d['loc_id']))


def get_sqlite_cursor(db_file):
    if not db_file.startswith('/'):
        db_file = os.path.join(os.getcwd(), db_file)

    conn = sqlite3.connect(db_file)
    return conn.cursor()


def load_memstore(load_from='.'):
    sum1 = summary.summarize(muppy.get_objects())
    if not load_from.startswith('/'):
        load_from = os.path.join(os.getcwd(), load_from)

    store_instance = store.InMemStore()
    store_instance.load(load_from)
    sum2 = summary.summarize(muppy.get_objects())
    diff = summary.get_diff(sum1, sum2)
    summary.print_(diff)
    #utils.memusage_overall()
    return store_instance


import socket
import struct


def ip2long(ip):
    """
    Convert an IP string to long
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


@task
def benchmark():
    store = load_memstore()
    for num in (10000, 50000, 100000):
        tit = timeit.Timer(lambda: store.find_location_by_ip(ip2long('165.69.2.3')))
        #import ipdb; ipdb.set_trace()
        print '{}: {}'.format(num, tit.timeit(number=num))

    for num in (10000, 50000, 100000):
        tit = timeit.Timer(lambda: store.find_location_by_ip(ip2long('54.252.136.40')))
        #import ipdb; ipdb.set_trace()
        print '{}: {}'.format(num, tit.timeit(number=num))


@task
def provision_memstore(store_instance=None, db_file='ipdb.sqlite', save_to='.'):
    if not store_instance:
        store_instance = store.InMemStore()

    if not save_to.startswith('/'):
        save_to = os.path.join(os.getcwd(), save_to)
        if not os.path.isdir(save_to):
            os.makedirs(save_to)

    cursor = get_sqlite_cursor(db_file)
    columns = [
        'ip_start',
        'loc_id',
        'country_code',
        'region_code',
        'city_name',
        'postal_code',
        'latitude',
        'longitude',
        'metro_code',
        'area_code',
    ]

    qry = '''SELECT b.ip_start, l.* from
    city_location l INNER JOIN
    city_blocks b ON
    l.loc_id = b.loc_id
    order by b.ip_start ASC'''

    for row in cursor.execute(qry):
        d = {}
        d = dict((col, row[idx]) for (idx, col) in enumerate(columns))
        store_instance.add_location_info(d['ip_start'], d)

    store_instance.dump(save_to)
    utils.memusage_overall()


@task
def provision(db_file='ipdb.sqlite', job='ic'):
    provision_ipstart_index(c)
    #provision_city_location(c)
