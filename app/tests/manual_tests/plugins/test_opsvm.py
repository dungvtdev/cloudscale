import setup_test
from plugins.opsvm import OpsVmService
import time


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

vm = {
    'name': 'testvm',
    'image': '601ea4f3-3973-4c96-9628-45fadb8165f7',
    'flavor': 'b6f1a774-a56c-47ec-b43c-ed67babe5da7',
    'selfservice': 'bb87469e-183e-4d89-a287-5397d6bac5e4',
    'provider_name': 'provider',
    'user_data': ''
}

t = ops.make_createvm_thread(vm)
t.start()

count = 1000
while(not t.is_finish() and count > 0):
    print(t.state)
    time.sleep(1)
    count = count - 1

print(t.state)
if(t.state == 'fail'):
    print(t.exception)

print('finish')