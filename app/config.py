import os

base_path = os.path.dirname(__file__)

LOG_FILE = os.path.join(base_path, 'cloudscale.log')
LOG_CONSOLE = True
LOG_LEVEL = 'DEBUG'
LOG_NAME = 'CloudScale'

DB_PATH = 'sqlite:///db.sqlite'

DEFAULT_PARAMS = {
    "pdgabp": {
        # tinh theo chu ky 1 lan lay du lieu (MONITOR_PERIOD_SECONDS)
        "data_length": 100,
        "update_in_time": 10,   # tinh nhu tren
        "neural_size": 15,
        "recent_point": 4,
        "periodic_number": 1
    },
    "monitor": {
        # "db_name": "cadvisor",
        'interval_minute': 4,
        "metric": ["cpu_usage_total", ]
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
    'max_fault_point': 8,
    'read_plugin': {
        'plugin': 'cadvisor_influxdb_series_read',
        'config': {
            'db': 'cadvisor'
        }
    },
    'cache_plugin': {
        'plugin': 'influxdb_series',
        'config': {
            'endpoint': '192.168.122.124'
        }
    }
}

# chu ky lay du lieu
MONITOR_PERIOD_SECONDS = 1

# so chu ky lay du lieu duoc du doan truoc
FORCAST_LENGTH = 1


API = {
    'version': ['v1', ],
    'address': '0.0.0.0',
    'port': 8008
}
