import setup_test
from modules.eventlog import EventLogFactory
import app as app_module
import os

basepath = os.path.dirname(__file__)

config = {
    'EVENTLOG': {
        'path': basepath,
        'prefix': 'eventlog',
        'maxBytes': 10000000,
        'backupCount': 3
    }
}

app = app_module.App()
app.config_from_dict(config)

factory = EventLogFactory()
factory.init_app(app)

log = factory.create('test')
log.write('group', 'create group')
log.write('scale', 'test scale')
print(log.get_log())
