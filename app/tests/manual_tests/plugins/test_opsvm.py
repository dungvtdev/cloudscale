import setup_test
from plugins.opsvm import OpsVmService
import time
import os


class App():
    pass


app = App()
app.config = {
    'OPS_ACCOUNT': {
        'auth_url': 'http://controller:5000/v3',
        'user_domain_name': 'default',
        'username': 'admin',
        'password': '123',
        'project_domain_name': 'default',
        'project_name': 'admin',
        'nova_version': '2.1'
    }
}

ops = OpsVmService()
ops.init_app(app)


def test_create():
    path_script = os.path.dirname(__file__)
    path_script = os.path.dirname(path_script)
    path_script = os.path.dirname(path_script)
    path_script = os.path.dirname(path_script)
    path_script = os.path.dirname(path_script)
    path_script = os.path.join(path_script, 'testbed/cloud.init/cloud_init.sh')

    with open(path_script, 'r') as f:
        user_data = f.read()

    vm = {
        'name': 'testvm',
        'image': 'd0111621-ab84-47c3-9f4c-ebae9a8e8c91',
        'flavor': 'b6f1a774-a56c-47ec-b43c-ed67babe5da7',
        'selfservice': 'bb87469e-183e-4d89-a287-5397d6bac5e4',
        'provider': 'provider',
        'user_data': user_data
    }

    t = ops.make_createvm_thread(vm)
    t.start()

    count = 1000
    while not t.is_finish() and count > 0:
        print(t.state)
        time.sleep(1)
        count = count - 1

    print(t.state)
    if t.state == 'fail':
        print(t.exception)

    print('finish')


def test_reboot():
    instance_id = 'a202fc26-90e0-410e-89e9-04841676e773'
    thrd = ops.make_reboot_thread({'instance_id': instance_id})
    thrd.start()
    thrd.join()
    print('success %s' % thrd.save_state)
    print(thrd.save_exception)


test_reboot()
