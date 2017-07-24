import setup_test
from bootstrap import app
from modules.healthcheck import HealthCheckController
import time

hc = HealthCheckController()
hc.init_app(app)

instance_id = '3a2c205d-bfb3-4009-ada4-dfc2ae8ef2a4'
try:
    while True:
        state = hc.reboot_server({'instance_id': instance_id})
        print(state)
        if state in ['fail', 'success']:
            break
        time.sleep(0.5)
except Exception as e:
    print e
