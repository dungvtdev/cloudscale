import requests
from core import DependencyModule
import json


class InfluxdbSeriesWritePlugin(DependencyModule):
    __module_name__ = 'influxdb_series_write'

    def on_register_app(self, app):
        pass

    def create(self, config):
        return InfluxdbSeriesWrite(config)


class WriteDriverBase():
    pass


class CpuTotalWriter(WriteDriverBase):
    _instance = None

    @classmethod
    def default(cls):
        if CpuTotalWriter._instance is None:
            CpuTotalWriter._instance = CpuTotalWriter()
        return CpuTotalWriter._instance

    def _create_database(self, endpoint, db):
        p = 'http://{endpoint}:8086/query?q=CREATE DATABASE {db}'
        p = p.format(endpoint=endpoint, db=db)
        r = requests.post(p)
        return r.status_code == 200

    def write_data(self, config, values):
        endpoint = config['endpoint']
        db = config['db']
        metric = config['metric']
        tags = config['tags']
        epoch = config['epoch']

        url = 'http://{endpoint}:8086/write?db={db}&epoch={epoch}'
        url = url.format(endpoint=endpoint, db=db, epoch=epoch)

        # build tags
        tags_str = ','.join("%s=%s" % (k, v) for k, v in tags.items())

        # create data
        base = '{metric},{tags} %s'.format(metric=metric, tags=tags_str)
        tmpl = base % 'value={value} {time}'

        data = '\n'.join(tmpl.format(value=line[1], time=line[0])
                         for line in values)

        r = requests.post(url, data=data)

        body = json.loads(r.text)
        if r.status_code == 404:
            if "database not found" in body.get("error", ""):
                self._create_database(endpoint, db)

                # khong lap lai truong hop so sanh database not found nua,
                # tranh bi lap vo han
                r = requests.post(url, data=data)

        if r.status_code != 204 and r.status_code != 200:
            raise Exception(body.get("error", ""))


class InfluxdbSeriesWrite():
    map = {
        'cpu_usage_total': CpuTotalWriter
    }

    def __init__(self, config):
        # config = {'endpoint', 'db', 'metric', 'tags'}
        self.config = config
        writerclass = self.map[config['metric']]()
        self.writer = writerclass.default()

    def write(self, values):
        # values = [(time, value),]
        try:
            self.writer.write_data(self.config, values)
        except Exception as e:
            raise e
