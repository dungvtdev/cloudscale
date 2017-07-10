import setup_test
from plugins.influxdb import InfluxdbSeriesReadPlugin

config = {
    'endpoint': '192.168.122.124',
    # 'db': 'test_db',
    'db': 'cadvisor',
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
values = reader.read(secs_length=100000)

print(values)


""" Test pandas series
"""
from core import seriesutils as su

pdseries = su.timevaluepair_to_pdseries(values)
# print(pdseries)

pdminute = su.resample(pdseries, 4)
series = su.get_newestseries(pdminute, 3)
is_finish = len(series) != len(pdminute)
print(series)
print(is_finish)
