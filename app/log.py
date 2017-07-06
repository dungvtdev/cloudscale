import logging
from logging.handlers import RotatingFileHandler
import sys
import os


class Log():
    def __init__(self):
        pass

    def init_app(self, app):
        LOG_FILE = app.config.get('LOG_FILE', None)
        LOG_CONSOLE = app.config.get('LOG_CONSOLE', False)
        LOG_LEVEL = app.config.get('LOG_LEVEL', 'DEBUG')
        LOG_NAME = app.config.get('LOG_NAME', __name__)

        log_level = getattr(logging, LOG_LEVEL)

        logger = logging.getLogger(LOG_NAME)
        logger.setLevel(log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        if LOG_CONSOLE:
            handler_console = logging.StreamHandler(sys.stdout)
            logger.addHandler(handler_console)

        if LOG_FILE:
            # create folder file
            directory = os.path.dirname(LOG_FILE)
            if directory and not os.path.exists(directory):
                os.mkdir(directory)
            handler_rotation_file = RotatingFileHandler(
                LOG_FILE, maxBytes=10000000, backupCount=3)
            handler_rotation_file.setFormatter(formatter)
            logger.addHandler(handler_rotation_file)

        app.logger = logger
