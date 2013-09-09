import bisect
import string
import os
import cPickle
import struct


class InMemStore(object):
    pack_fmt = '=iiiff'
    __name__ = 'InMemStore'

    def __init__(self):
        self.ip_start_idx = []
        self.location_info = []
        self.region_name_index = []
        self.region_name = []
        self.city_name = []
        self.postal_code = []

    def index_of(self, attr_name, attr_val):
        lst = getattr(self, attr_name)

        try:
            return lst.index(attr_val)
        except ValueError:
            lst.append(attr_val)
            return len(lst) - 1

    def add_location_info(self, loc_info):
        self.ip_start_idx.append(int(loc_info['b.ip_start']))
        country_region_code = '{}.{}'.format(loc_info['l.country_code'], loc_info['l.region_code'])
        region_idx = -1
        try:
            region_idx = self.region_name_index.index(country_region_code)
        except ValueError:
            pass

        info = [
            region_idx,
            self.index_of('city_name', loc_info['l.city_name']),
            self.index_of('postal_code', loc_info['l.postal_code']),
            loc_info['l.longitude'],
            loc_info['l.latitude']
        ]

        self.location_info.append(
            struct.pack(self.pack_fmt, *info))

    def add_region_name(self, region_info):
        self.region_name_index.append(
            region_info['country_region_code']
        )
        self.region_name.append(
            (region_info['country_name'], region_info['region_name'])
        )

    def find_location_by_ip(self, ip_int):
        i = bisect.bisect_right(self.ip_start_idx, ip_int)
        info_bin = self.location_info[i-1]
        region_idx, city_name_idx, postal_code_idx, longtitude, latitude\
            = struct.unpack(self.pack_fmt, info_bin)

        ret = {
            'region_name': None,
            'city_name': self.city_name[city_name_idx],
            'postal_code': self.postal_code[postal_code_idx],
            'longtitude': longtitude,
            'latitude': latitude
        }

        if region_idx >= 0:
            ret['region_name'] = self.region_name[region_idx]

        return ret

    def shrink(self):
        ip_start_idx = self.ip_start_idx
        location_info = self.location_info

        self.ip_start_idx = tuple(ip_start_idx)
        self.location_info = tuple(location_info)

        del ip_start_idx
        del location_info

    def dump(self, save_to):
        self.shrink()
        with open(save_to, 'wb') as f:
            cPickle.dump(self, f)

    @staticmethod
    def load(path):
        with open(path, 'rb') as f:
            return cPickle.load(f)
