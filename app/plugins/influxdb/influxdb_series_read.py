import json
import requests

from core import DependencyModule
from core.exceptions import NotEnoughParams


class InfluxdbSeriesReadPlugin(DependencyModule):
    __module_name__ = 'influxdb_series_read'

    def on_register_app(self, app):
        pass

    def create(self, config):
        return InfluxdbSeriesRead(config)


class ReadDriverBase():
    pass


class CPUTotalRead(ReadDriverBase):
    _instance = None
    _filters = ['root_container_filter', ]

    @classmethod
    def default(cls):
        if CPUTotalRead._instance is None:
            CPUTotalRead._instance = CPUTotalRead()
        return CPUTotalRead._instance

    """ Filters
    """

    def root_container_filter(self, serie):
        return serie["tags"]["container_name"] == '/'

    def generate_query(self, endpoint, metric, epoch,
                       secs_from, secs_to, secs_length):
        use_length = (secs_from is None or secs_to is None) and secs_length
        if use_length:
            if secs_from is not None:
                q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= {utc_begin}{epoch} AND time <= {utc_end}{epoch} GROUP BY "container_name" fill(null)'
                q = q.format(metric=metric, utc_begin=secs_from,
                             utc_end=secs_from + secs_length, epoch=epoch)
            elif secs_to is not None:
                q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= {utc_begin}{epoch} AND time <= {utc_end}{epoch} GROUP BY "container_name" fill(null)'
                q = q.format(metric=metric, utc_begin=secs_to - secs_length,
                             utc_end=secs_to, epoch=epoch)
            else:
                q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= now() - {secs_length}{epoch} GROUP BY "container_name" fill(null)'
                q = q.format(
                    metric=metric, secs_length=secs_length, epoch=epoch)
        else:
            q = 'SELECT derivative("value", 1s)/1000000000 FROM {metric} WHERE time >= {utc_begin}{epoch} AND time <= {utc_end}{epoch} GROUP BY "container_name" fill(null)'
            q = q.format(metric=metric, utc_begin=secs_to - secs_length,
                         utc_end=secs_to, epoch=epoch)
        print(q)
        return q

    def read_data(self, config, secs_from=None, secs_to=None, secs_length=None):
        # validate
        if not (secs_from or secs_to or secs_length):
            raise NotEnoughParams(
                'secs_from, secs_to, secs_length are all None')

        endpoint = config['endpoint']
        db = config['db']
        metric = config['metric']
        epoch = config['epoch']
        filter_setting = config['filter']

        # generate query
        query = self.generate_query(endpoint=endpoint, metric=metric,
                                    epoch=epoch, secs_from=secs_from,
                                    secs_to=secs_to, secs_length=secs_length)
        url = 'http://{endpoint}:8086/query'.format(endpoint=endpoint)
        params = {
            'db': db,
            'epoch': epoch,
            'q': query
        }
        r = requests.get(url, params)

        if r.status_code == 200:
            return self.extract_data(r.text, filter_setting)
        else:
            body = json.loads(r.text)
            raise Exception(body.get("error", ""))

    def extract_data(self, text, filter_setting):
        if filter_setting in self._filters:
            filter_func = getattr(self, filter_setting)
            jdata = json.loads(text)
            if jdata.get("results", None) is None \
                    or not jdata["results"][0]:
                raise Exception('Got Data is None')

            series = jdata["results"][0]["series"]
            values_raw = next(s["values"] for s in series if filter_func(s))

            # da chuyen ve dang [(time_secs, value), ]
            values = values_raw
            return values
        else:
            raise Exception('Unknown filter %s' % filter_setting)


class InfluxdbSeriesRead():
    map = {
        'cpu_usage_total': CPUTotalRead
    }

    def __init__(self, config):
        self.config = config
        readerclass = self.map[config['metric']]()
        self.reader = readerclass.default()

    def read(self, secs_from=None, secs_to=None, secs_length=None):
        try:
            return self.reader.read_data(self.config, secs_from=secs_from,
                                         secs_to=secs_to,
                                         secs_length=secs_length)
        except Exception as e:
            raise e
