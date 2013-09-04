import bisect
import string
import os
import cPickle
import struct
import array


class InMemStore(object):
    pack_fmt = '=iff'
    __name__ = 'InMemStore'

    def __init__(self):
        self.ip_start_idx = []
        self.location_info = []
        self.location_detail = []
        self.location_dict = {}

    def add_location_info(self, ip_start, loc_info):
        self.ip_start_idx.append(int(ip_start))

        key_tuple = (
            loc_info['region_code'],
            loc_info['country_code'],
            loc_info['metro_code'],
            loc_info['city_name'],
            loc_info['postal_code'],
            loc_info['area_code']
        )

        key = string.join(key_tuple, '^')

        detail_idx = self.location_dict.get(key)
        if not detail_idx:
            detail_idx = len(self.location_detail)
            self.location_dict[key] = detail_idx
            self.location_detail.append(key_tuple)

        self.location_info.append(
            struct.pack(
                self.pack_fmt, loc_info['loc_id'], loc_info['longitude'], loc_info['latitude'])
        )

    def find_location_by_ip(self, ip_int):
        i = bisect.bisect_right(self.ip_start_idx, ip_int)
        s = self.location_info[i-1]
        loc_id, longtitude, latitude = struct.unpack(self.pack_fmt, s)

        return {
            'loc_id': loc_id,
            'longtitude': longtitude,
            'latitude': latitude,
            'detail': self.location_detail[detail_idx]
        }

    def shrink(self):
        ip_start_idx = self.ip_start_idx
        location_info = self.location_info
        location_detail = self.location_detail

        self.ip_start_idx = tuple(ip_start_idx)
        self.location_info = tuple(location_info)
        self.location_detail = tuple(location_detail)

        del ip_start_idx
        del location_info
        del location_detail
        # intermediate dictionary
        del self.location_dict

    def dump(self, save_to):
        self.shrink()
        path_ip_start_idx = os.path.join(
            save_to,
            'ip_start_idx.pickle'
        )

        path_location_info = os.path.join(
            save_to,
            'location_info.pickle'
        )

        path_location_detail = os.path.join(
            save_to,
            'location_detail.pickle'
        )

        for path, o in [
                (path_ip_start_idx, self.ip_start_idx),
                (path_location_info, self.location_info),
                (path_location_detail, self.location_detail)]:

            with open(path, 'wb') as f:
                cPickle.dump(o, f)

    def load(self, save_to):
        path_ip_start_idx = os.path.join(
            save_to,
            'ip_start_idx.pickle'
        )

        path_location_info = os.path.join(
            save_to,
            'location_info.pickle'
        )

        path_location_detail = os.path.join(
            save_to,
            'location_detail.pickle'
        )

        for path, attr in [
                (path_ip_start_idx, 'ip_start_idx'),
                (path_location_info, 'location_info'),
                (path_location_detail, 'location_detail')]:

            with open(path, 'rb') as f:
                setattr(self, attr, cPickle.load(f))
