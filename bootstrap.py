import app as app_module
import config
import log
from modules.info import InfoManager


def configure_log(app):
    logger = log.Log()
    logger.init_app(app)


def configure_info_manager(app):
    infomanager = InfoManager()
    infomanager.init_app(app)


app = application = app_module.App()
application.config_from_module(config)

configure_log(application)
configure_info_manager(application)
