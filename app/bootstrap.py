import app as app_module
import config
import log
from plugins.info import InfoManager
from plugins.sqlbackend import SQLBackend
from plugins.influxdb import CadvisorInfluxdbSeriesReadPlugin, \
    InfluxdbSeriesPlugin
from modules.group import GroupUtils
from modules.controller import Controller


def configure_log(app):
    logger = log.Log()
    logger.init_app(app)


def configure_info_manager_plugin(app):
    infomanager = InfoManager()
    infomanager.init_app(app)


def configure_sqlbackend_plugin(app):
    sqlbackend = SQLBackend()
    sqlbackend.init_app(app)
    sqlbackend.create_all()


def configure_influxdb_plugin(app):
    influxdbseriesread = CadvisorInfluxdbSeriesReadPlugin()
    influxdbseriesread.init_app(app)

    influxdbserieswrite = InfluxdbSeriesPlugin()
    influxdbserieswrite.init_app(app)


def configure_group_module(app):
    grouputils = GroupUtils()
    grouputils.init_app(app)


def configure_controller(app):
    controller = Controller()
    controller.init_app(app)


app = application = app_module.App()
application.config_from_module(config)

configure_log(application)
configure_info_manager_plugin(application)
configure_sqlbackend_plugin(application)
configure_influxdb_plugin(application)

configure_group_module(application)
configure_controller(application)

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
