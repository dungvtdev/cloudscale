import os

base_path = os.path.dirname(__file__)

LOG_FILE = os.path.join(base_path, 'cloudscale.log')
LOG_CONSOLE = True
LOG_LEVEL = 'DEBUG'
LOG_NAME = 'CloudScale'

DB_PATH = 'sqlite:///db.sqlite'

DEFAULT_PARAMS = {
    "pdgabp": {
        # tinh theo chu ky 1 lan lay du lieu (interval_minute)
        "data_length": 100,
        "update_in_time": 120,  # tinh nhu tren
        "neural_size": 15,
        "recent_point": 4,
        "periodic_number": 1,
        "predict_length": 1,
        'cross_rate': 0.5,
        'mutation_rate': 0.04,
        'pop_size': 50
    },
    "monitor": {
        # "db_name": "cadvisor",
        'interval_minute': 4,
        "metric": "cpu_usage_total"
    },
    "scale": {
        # 'max_scale_vm': 1,
        'app_port': 8000
    },
    "group": [
        "pdgabp", "monitor", "scale"
    ],
    "vm": [
        # "monitor"
    ]
}

OPS_ACCOUNT = {
    'auth_url': 'http://controller:5000/v3',
    'user_domain_name': 'default',
    'username': 'admin',
    'password': '123',
    'project_domain_name': 'default',
    'project_name': 'admin',
    'nova_version': '2.1'
}

MONITOR = {
    'max_batch_size': 10000,
    'max_fault_point': 10,
    'read_plugin': {
        'plugin': 'cadvisor_influxdb_series_read',
        'config': {
            'db': 'cadvisor'
        }
    },
    'cache_plugin': {
        'plugin': 'influxdb_series',
        'config': {
            'endpoint': 'localhost',
            'db': 'cache_%s',
            # 'endpoint': '127.0.0.1'
        }
    }
}

FORECAST = {
    'threshold': 0.1,
    'fs': 360,
    'predict_plugin': 'predictplugin',
    'feeder_plugin': 'feederplugin',
}

GROUPCACHE = {
    'cache_plugin': {
        'plugin': 'influxdb_series',
        'config': {
            'endpoint': 'localhost',
            'db': 'cache_%s',
            # 'endpoint': '127.0.0.1'
        }
    },
}

SCALE = {
    'scale_controller': {
        'cpu_usage_total': {
            'controller': 'simple_scale',
            'config': {
                'max_value': 0.5,
                'sum_length': 5,
            }
        }
    },
    # 'max_scale': 2,
    'warm_up': 2,
    'try_scale_when_fail': 2
    # 'port': 8080
}

API = {
    'version': ['v1', ],
    'address': '0.0.0.0',
    'port': 8008
}

LOADBALANCER = {
    'ip': 'localhost',
    'port_begin': 8888,
    'config_path': '/etc/haproxy/haproxy.cfg',
}

EVENTLOG = {
    'path': base_path,
    'prefix': 'eventlog',
    'maxBytes': 10000000,
    'backupCount': 3
}
