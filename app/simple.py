from bootstrap import app

app.controller.run()

instances = [
    {'instance_id': '', 'endpoint': ''}
]
group_dict = {
    'user_id': 'dung',
    'name': 'group1',
    'desc': '',
    'image': 'image1',
    'flavor': 'm1',
    'selfservice': 's1',
    'provider': 'p1',
    'user_data': '',
    'instances': instances
}
