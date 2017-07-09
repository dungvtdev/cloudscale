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
        "db_name": "cadvisor",
        "metric": "cpu_usage_total"
    },
    "group": [
        "pdgabp", "monitor"
    ],
    "vm": [
        "monitor"
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

# chu ky lay du lieu
MONITOR_PERIOD_SECONDS = 1

# so chu ky lay du lieu duoc du doan truoc
FORCAST_LENGTH = 1
