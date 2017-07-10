from core import DependencyModule


class InfluxdbSeriesReadPlugin(DependencyModule):
    __module_name__ = 'influxdb_series_read'

    def on_register_app(self, app):
        pass

    def create(self, config):
        return InfluxdbSeriesRead(config)


class InfluxdbSeriesRead():
    def __init__(self, config):
        self.endpoint = config['endpoint']
        self.dbname = config['dbname']
        self.max_fault_minute = config.get('max_fault_minute', 0)
        self.batch_size = config.get('batch_size', 0)


class ReadDriverBase():
    pass


class CPUTotalRead(ReadDriverBase):
    def __init__(self, data):
        pass
