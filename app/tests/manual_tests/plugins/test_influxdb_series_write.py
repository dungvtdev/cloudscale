import time
import setup_test
from plugins.influxdb import InfluxdbSeriesWritePlugin


config = {
    'endpoint': '192.168.122.124',
    'db': 'test_db',
    'metric': 'cpu_usage_total',
    'epoch': 's',
    'tags': {
        'container_name': '/',
    }
}


class App():
    pass


app = App()

writerservice = InfluxdbSeriesWritePlugin()
writerservice.init_app(app)

writer = writerservice.create(config)

values = [(i, int(time.time() - i) * 1000000000) for i in range(1000)]

writer.write(values)
