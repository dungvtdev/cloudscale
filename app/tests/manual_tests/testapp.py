import sys
import os

base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
base_path = os.path.abspath(base_path)

sys.path.append(base_path)

from bootstrap import app

group_dict = {
    'name': 'testvm',
    'user_id': '',
    'image': '601ea4f3-3973-4c96-9628-45fadb8165f7',
    'flavor': 'b6f1a774-a56c-47ec-b43c-ed67babe5da7',
    'selfservice': 'bb87469e-183e-4d89-a287-5397d6bac5e4',
    'provider': 'provider',
    'user_data': '',
    'instances': [{
        'endpoint': '192.168.122.188',
        # 'endpoint': '192.168.122.224',
        'instance_id': 'a202fc26-90e0-410e-89e9-04841676e773'
    }],
    'data_length': 10,
    'update_in_time': 20,
    'metric': 'cpu_usage_total',
    'max_scale_vm': 1
}
app.controller.create_group(group_dict)
