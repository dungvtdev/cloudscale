import setup_test
from bootstrap import app
import time

config = {
    'name': 'test_name',
    'controller': 'simple_scale',
    'config': {}
}

group_config = {
    'name': 'testvm',
    'user_id': '',
    'image': '601ea4f3-3973-4c96-9628-45fadb8165f7',
    'flavor': 'b6f1a774-a56c-47ec-b43c-ed67babe5da7',
    'selfservice': 'bb87469e-183e-4d89-a287-5397d6bac5e4',
    'provider': 'provider',
    'user_data': ''
}

scalecontroller = app.scalefactory.create(group_config, config)

while True:
    time.sleep(0.5)
    scalecontroller.test_scale_up()
    rl = scalecontroller.receive()
    print(rl)
    print(scalecontroller.instances)
    if rl and (rl['state'] == 'success' or rl['state'] == 'fail'):
        break

time.sleep(3)

while True:
    time.sleep(0.5)
    scalecontroller.test_scale_down()
    rl = scalecontroller.receive()
    print(rl)
    print(scalecontroller.instances)
    if rl and (rl['state'] == 'success' or rl['state'] == 'fail'):
        break
