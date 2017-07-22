import setup_test
from bootstrap import app
import time

config = {
    'controller': 'simple_scale',
    'config': {
        'max_value': 0.6,
        'sum_length': 10,
    },
    'max_scale': 2,
    'warm_up_minutes': 2
}

group_config = {
    'name': 'testvm',
    'user_id': '',
    'image': '601ea4f3-3973-4c96-9628-45fadb8165f7',
    'flavor': 'b6f1a774-a56c-47ec-b43c-ed67babe5da7',
    'selfservice': 'bb87469e-183e-4d89-a287-5397d6bac5e4',
    'provider': 'provider',
    'user_data': '',
    'instances': ['123']
}

scalecontroller = app.scalefactory.create(group_config, config)


def test_simple():
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


def test_2():
    d = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.2, 0.5, 0.3, 0.2, 0.1, 0.2, 0.1, 0.3, 0.2, 0.1, 0.3, 0.1, 0.2, 0.1]
    while len(d) > 1:
        n = d.pop(0)
        p = d[0]
        scalecontroller.add_point(n, p)
        time.sleep(1)

test_2()
