import setup_test
from plugins.influxdb import InfluxdbSeriesReadPlugin

config = {
    'endpoint': '192.168.122.124',
    'db': 'test_db',
    'metric': 'cpu_usage_total',
    'epoch': 's',
    'filter': 'root_container_filter',
}


class App():
    pass


app = App()

read_plugin = InfluxdbSeriesReadPlugin()
read_plugin.init_app(app)

reader = read_plugin.create(config)
values = reader.read(secs_length=10000)

print(values)
