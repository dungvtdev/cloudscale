from core import DependencyModule


class InfluxdbSeriesWritePlugin(DependencyModule):
    __module_name__ = 'influxdb_series_write'

    def on_register_app(self, app):
        pass

    def create(self, config):
        return InfluxdbSeriesWrite(config)


class InfluxdbSeriesWrite():
    def __init__(self, config):
        pass
