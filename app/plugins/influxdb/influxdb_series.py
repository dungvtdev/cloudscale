import requests
from core import DependencyModule
import json


class InfluxdbSeriesPlugin(DependencyModule):
    __module_name__ = 'influxdb_series'

    def on_register_app(self, app):
        pass

    def create(self, config):
        return SimpleInfluxdb(config)


class InfluxdbDriverBase():
    pass


class SimpleInfluxdbService(InfluxdbDriverBase):
    _instance = None

    @classmethod
    def default(cls):
        if SimpleInfluxdbService._instance is None:
            SimpleInfluxdbService._instance = SimpleInfluxdbService()
        return SimpleInfluxdbService._instance

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

        if r.status_code == 404:
            # body = json.loads(r.text)
            # if "database not found" in body.get("error", ""):
            if "database not found" in r.text:
                self._create_database(endpoint, db)

                # khong lap lai truong hop so sanh database not found nua,
                # tranh bi lap vo han
                r = requests.post(url, data=data)

        if r.status_code != 204 and r.status_code != 200:
            # raise Exception(body.get("error", ""))
            raise Exception(r.text)

    def get_read_query(self, config, time_from, time_to, time_length):
        metric = config['metric']
        tags = config['tags']
        epoch = config['epoch']

        conditions = ' AND '.join(["%s='%s'" % (k, v)
                                   for k, v in tags.items()])

        use_length = (time_from is None or time_to is None) and time_length
        if use_length:
            if time_from is not None:
                q = 'SELECT value from {metric} where time >= {time_from}{epoch} AND time <= {time_to}{epoch} AND {conditions}'
                q = q.format(metric=metric, epoch=epoch, conditions=conditions,
                             time_from=time_from, time_to=time_from + time_length)
            elif time_to is not None:
                q = 'SELECT value from {metric} where time >= {time_from}{epoch} AND time <= {time_to}{epoch} AND {conditions}'
                q = q.format(metric=metric, epoch=epoch, conditions=conditions,
                             time_from=time_to - time_length, time_to=time_to)
            else:
                q = 'SELECT value from {metric} where time >= now() - {time_length}{epoch} AND {conditions}'
                q = q.format(metric=metric, epoch=epoch,
                             conditions=conditions, time_length=time_length)
        else:
            q = 'SELECT value from {metric} where time >= {time_from}{epoch} AND time <= {time_to}{epoch} AND {conditions}'
            q = q.format(metric=metric, epoch=epoch, conditions=conditions,
                         time_from=time_from, time_to=time_to)
        return q

    def read_data(self, config, time_from=None, time_to=None, time_length=None):
        query = self.get_read_query(config, time_from, time_to, time_length)
        params = {
            'db': config['db'],
            'epoch': config['epoch'],
            'q': query
        }
        url = 'http://{endpoint}:8086/query'.format(
            endpoint=config['endpoint'])
        r = requests.get(url, params)

        if r.status_code == 200:
            body = json.loads(r.text)
            try:
                return body['results'][0]['series'][0]['values']
            except Exception as e:
                raise Exception('Data not correct form or null')
        else:
            raise Exception(r.text)

    def read_value(self, tag):
        return self.read_write_value('read', tag)

    def write_value(self, tag, value):
        self.read_write_value('write', tag, value)

    def read_write_value(self, action, tag, *args):
        endpoint = config['endpoint']
        db = config['db']
        metric = config['metric']
        tags = config['tags']
        tags['tag'] = tag
        epoch = config['epoch']

        # build tags

        if action == 'read':
            tags_str = ' AND '.join("%s=%s" % (k, v) for k, v in tags.items())
            url = 'http://{endpoint}:8086/query'.format(endpoint=endpoint)
            query = 'SELECT value from {metric} where {tags_str}'.format(
                metric=metric, tags_str=tags_str)
            params = {
                'epoch': epoch,
                'db': db,
                'q': query
            }
            r = requests.get(url, params=params)
            try:
                value = ['results'][0]['series'][0]['values'][0][1]
                return value
            except Exception as e:
                raise Exception('Get error')
        else:
            tags_str = ','.join("%s=%s" % (k, v) for k, v in tags.items())
            url = 'http://{endpoint}:8086/write?db={db}&epoch={epoch}'
            url = url.format(endpoint=endpoint, db=db, epoch=epoch)
            value = args[0]
            data = '{metric},{tags} value={value} 0'.format(
                metric=metric, tags=tags_str, value=value)
            r = requests.post(url, data=data)
            success = r.status_code == 200 or r.status_code == 204
            if not success:
                raise Exception('Error when write value')


class SimpleInfluxdb():

    def __init__(self, config):
        # config = {'endpoint', 'db', 'metric', 'tags'}
        self.config = config
        self.service = SimpleInfluxdbService.default()

    def write(self, values):
        # values = [(time, value),]
        try:
            self.service.write_data(self.config, values)
        except Exception as e:
            raise e

    def read(self, time_from=None, time_to=None, time_length=None):
        try:
            return self.service.read_data(self.config, time_from=time_from,
                                          time_to=time_to, time_length=time_length)
        except Exception as e:
            raise e
