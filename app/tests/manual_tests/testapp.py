import sys
import os

base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
base_path = os.path.abspath(base_path)

sys.path.append(base_path)

from bootstrap import app

group_dict = {
    'name': 'test_vm',
    'user_id': 'u1',
    'image': 'i1',
    'flavor': 'f1',
    'selfservice': 's1',
    'provider': 'p1',
    'instances': [{
        'endpoint': '192.168.122.124',
        'instance_id': 'is1'
    }]
}
app.controller.create_group(group_dict)
