import app as app_module
import config
import log
from plugins.info import InfoManager
from plugins.sqlbackend import SQLBackend
from plugins.influxdb import CadvisorInfluxdbSeriesReadPlugin, \
    InfluxdbSeriesPlugin
from plugins.forecast import PredictPlugin, FeederPlugin
from plugins.opsvm import OpsVmService
from plugins.haproxy import HAProxyCtrl
from modules.group import GroupUtils
from modules.controller import Controller
from modules.scale import ScaleFactory
from modules.eventlog import EventLogFactory
from modules.healthcheck import HealthCheckController


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


def configure_predict_plugin(app):
    predict = PredictPlugin()
    predict.init_app(app)

    feeder = FeederPlugin()
    feeder.init_app(app)


def configure_opsclient_plugin(app):
    opsvm = OpsVmService()
    opsvm.init_app(app)


def configure_haproxy_plugin(app):
    haproxy = HAProxyCtrl()
    haproxy.init_app(app)


def configure_group_module(app):
    grouputils = GroupUtils()
    grouputils.init_app(app)


def configure_healthcheck_module(app):
    hc = HealthCheckController()
    hc.init_app(app)


def configure_controller(app):
    controller = Controller()
    controller.init_app(app)

    scalectrl = ScaleFactory()
    scalectrl.init_app(app)


def configure_eventlog(app):
    eventlog = EventLogFactory()
    eventlog.init_app(app)


def configure_api(app):
    from modules.api import APIHandler

    api = APIHandler()
    api.init_app(app)


app = application = app_module.App()
application.config_from_module(config)

configure_log(application)
configure_info_manager_plugin(application)
configure_sqlbackend_plugin(application)
configure_influxdb_plugin(application)
configure_predict_plugin(application)
configure_opsclient_plugin(application)
configure_eventlog(application)
configure_haproxy_plugin(application)
configure_healthcheck_module(application)
configure_group_module(application)
configure_controller(application)
configure_api(application)

# app.apihandler.listen()
