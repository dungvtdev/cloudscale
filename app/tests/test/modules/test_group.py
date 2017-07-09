import os

import sys

base_path = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))))
base_path = os.path.abspath(base_path)

sys.path.append(base_path)

from bootstrap import app
from plugins import sqlbackend as sql
from plugins.info import InfoManager
from modules.group import GroupUtils
from core.exceptions import ExistsException

import unittest

path = os.path.join(os.path.dirname(__file__), 'test.db.sqlite')

conf = {
    'DB_PATH': 'sqlite:///%s' % path
}

app.config_from_dict(conf)

sqlbackend = sql.SQLBackend()
sqlbackend.init_app(app)
sqlbackend.create_all()

infomanager = InfoManager()
infomanager.init_app(app)

group = GroupUtils()
group.init_app(app)

group_dict = {
    'user_id': 'user',
    'name': 'name',
}
vm_dicts = [
    {
        'instance_id': 'iid1',
        'endpoint': 'endpoint1',
        'user_id': 'u1'
    },
    {
        'instance_id': 'iid1',
        'endpoint': 'endpoint1',
        'user_id': 'u1'
    }
]

try:
    # tao mot group moi
    g_id = group.db_create_group(group_dict)
    g = group.db_get_group({'group_id': g_id})
    assert g != None
    assert g.data_length > 0
    assert g.created != None

    group.db_drop_group({'group_id': g_id})

    # drop vm chua ton tai khong bao loi
    group.db_drop_vm(vm_dicts[0])

    # create vm
    group.db_create_vm(vm_dicts[0])

    # bao loi khi tao them vm only new
    try:
        group.db_create_vms_onlynew(vm_dicts)
    except ExistsException as e:
        pass
    assert e
finally:
    os.remove(path)