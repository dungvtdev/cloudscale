import logging
from logging.handlers import RotatingFileHandler
import os
from core import DependencyModule


class EventLogFactory(DependencyModule):
    __module_name__ = 'eventlogfactory'

    def on_register_app(self, app):
        pass

    def create(self, name):
        return EventLog(self._app, name)


class EventLog(object):
    def __init__(self, app, name):
        config = app.config['EVENTLOG']
        name_prefix = config['prefix']
        path = config['path']
        maxBytes = config['maxBytes']
        backupCount = config['backupCount']

        logname = '%s_%s.log' % (name_prefix, name)
        path = os.path.join(path, logname)
        self.path = path

        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.mkdir(directory)
        handler_rotation_file = RotatingFileHandler(
            path, maxBytes=maxBytes, backupCount=backupCount)

        formatter = logging.Formatter(
            '%(asctime)s|%(message)s'
        )

        handler_rotation_file.setFormatter(formatter)

        logger = logging.getLogger(logname)
        logger.setLevel(logging.INFO)

        logger.addHandler(handler_rotation_file)

        self.logger = logger

    def write(self, tag, message):
        self.logger.info('%s|%s' % (tag, message))

    def get_log(self):
        with open(self.path, 'r') as f:
            text = f.read()
            return text
