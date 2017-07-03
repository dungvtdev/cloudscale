import app
import config
import log


def configure_log(app):
    logger = log.Log()
    logger.init_app(app)


application = app.App()
application.config_from_module(config)

configure_log(application)