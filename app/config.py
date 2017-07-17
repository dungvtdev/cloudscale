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
        "update_in_time": 1000  ,  # tinh nhu tren
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
        'interval_minute': 1,
        "metric": "cpu_usage_total"
    },
    "group": [
        "pdgabp", "monitor"
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
    'max_fault_point': 2,
    'read_plugin': {
        'plugin': 'cadvisor_influxdb_series_read',
        'config': {
            'db': 'cadvisor'
        }
    },
    'cache_plugin': {
        'plugin': 'influxdb_series',
        'config': {
            'endpoint': '192.168.122.124',
            'db': 'cache_%s',
            # 'endpoint': '127.0.0.1'
        }
    }
}

FORECAST = {
    'threshold': 0.1,
    'fs': 144,
    'predict_plugin': 'predictplugin',
    'feeder_plugin': 'feederplugin',
}

GROUPCACHE = {
    'cache_plugin': {
        'plugin': 'influxdb_series',
        'config': {
            'endpoint': '192.168.122.124',
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
                'max_value': 0.6,
                'sum_length': 10,
            }
        }
    },
    'max_scale': 2,
    'warm_up': 2
}
