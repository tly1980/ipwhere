import timeit
import os
import logging
import logging.config

import yaml
from fabric.api import task

import ipwhere


logging.config.dictConfig(
    yaml.load(open('logging.yaml', 'r')))


def to_abs_path(path):
    if path.startswith('.'):
        path = os.path.join(os.getcwd(), path)

    return path


@task
def benchmark(path='./data/inmemstore.pickle'):
    path = to_abs_path(path)
    store = ipwhere.store.InMemStore.load(path)
    for num in (10000, 50000, 100000):
        tit = timeit.Timer(lambda: store.find_location_by_ip(
            ipwhere.utils.ip2long('165.69.2.3')))
        print '{}: {}'.format(num, tit.timeit(number=num))

    for num in (10000, 50000, 100000):
        tit = timeit.Timer(lambda: store.find_location_by_ip(
            ipwhere.utils.ip2long('54.252.136.40')))
        print '{}: {}'.format(num, tit.timeit(number=num))


@task
def provision_memstore(db_file='./data/ipdb.sqlite', save_to='./data/inmemstore.pickle'):
    db_file = to_abs_path(db_file)
    save_to = to_abs_path(save_to)

    pv = ipwhere.provision.Provisioner(db_file)
    memstore = ipwhere.store.InMemStore()
    pv.provision(memstore)
    memstore.dump(save_to)
