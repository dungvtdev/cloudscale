from core import requests_wrapper as requests
from requests.exceptions import ConnectionError, Timeout
import os
import time

basepath = os.path.dirname(__file__)
filelog = os.path.join(basepath, 'health.log')


def log(msg):
    print(msg)
    with open(filelog, 'a') as f:
        f.write('%s\n' % msg)


def start_healthcheck(group_dict, app):
    vm = group_dict['instances'][0]
    print('start_health check')
    n_interval = 15
    warm_up = 240
    while True:
        interval = n_interval
        # ping influxsrv

        url = 'http://%s:8086/ping' % vm['endpoint']
        need_reboot = False
        try:
            r = requests.get(url)
            if r.status_code != 204:
                need_reboot = True
        except (ConnectionError, Timeout) as e:
            print(e)
            need_reboot = True

        if need_reboot:
            try:
                state = app.healthcheck.reboot_server(vm)
                if state == 'fail':
                    # thu reboot lai ngay neu fail
                    # app.healthcheck.reboot_server(vm)
                    log('fail to reboot monitor vm, retry')
                elif state == 'success':
                    interval = warm_up
                    log('reboot monitor vm state %s' % state)
            except Exception as e:
                log('fail to reboot monitor vm %s' % e)

        time.sleep(interval)
