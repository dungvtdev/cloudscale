import time
import setup_test
from plugins.influxdb import InfluxdbSeriesPlugin


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

service = InfluxdbSeriesPlugin()
service.init_app(app)

driver = service.create(config)

values = [(i, int(time.time() - i) * 1000000000) for i in range(1000)]

driver.write(values)

read_values = driver.read(time_length=1000)
print(read_values)
