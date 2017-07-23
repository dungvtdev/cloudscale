import setup_test
from plugins.haproxy import HAProxyCtrl


class App():
    def __init__(self):
        self.config = {
            'LOADBALANCER': {
                'ip': 'localhost',
                'port_begin': 1120,
                'config_path': '/etc/haproxy/haproxy.cfg'
            }
        }


app = App()
haproxy = HAProxyCtrl()
haproxy.init_app(app)

haproxy.add_server('192.168.122.188', 8000, 8888)
