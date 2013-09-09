import string
import sqlite3
import logging


class Provisioner(object):

    CITY_LOCATION_COL = [
        'b.ip_start',
        'l.loc_id',
        'l.country_code',
        'l.region_code',
        'l.city_name',
        'l.postal_code',
        'l.latitude',
        'l.longitude',
        'l.metro_code',
        'l.area_code',
    ]

    REGION_COLUMNS = [
        'country_region_code',
        'country_name',
        'region_name'
    ]

    def __init__(self, db_file):
        conn = sqlite3.connect(db_file)
        self.cursor = conn.cursor()
        self.logger = logging.getLogger(__name__)

    def city_locations(self):
        return self.cursor.execute("""SELECT
            {}
            from
            city_blocks b
            INNER JOIN
            city_location l
            ON b.loc_id = l.loc_id
            order by b.ip_start ASC""".format(
            string.join(self.CITY_LOCATION_COL, ',')))

    def region_names(self):
        return self.cursor.execute("""SELECT r.country_code || '.' || r.region_code,
            c.country_name,
            r.region_name
            from region_names r LEFT OUTER JOIN country_blocks c ON
            r.country_code = c.country_code
            group by r.country_code, r.region_code, r.region_name""")

    def provision(self, store):
        self.store = store
        self.provision_region_names()
        self.provision_city_location()

    def provision_region_names(self):
        self.logger.info("begin provisioning region name")
        for row in self.region_names():
            d = {}
            d = dict((col, row[idx]) for (idx, col) in enumerate(
                self.REGION_COLUMNS))
            self.store.add_region_name(d)
        self.logger.info("finish provisioning region name")

    def provision_city_location(self):
        self.logger.info("begin provisioning city_locations name")
        i = 0
        for row in self.city_locations():
            d = {}
            d = dict((col, row[idx]) for (idx, col) in enumerate(
                self.CITY_LOCATION_COL))
            self.store.add_location_info(d)
            i += 1
            if not (i % 10000):
                self.logger.info('finish city_locations number: %s' % i)
        self.logger.info("finish provisioning city_locations name")
