from core import DependencyModule
from .predict import Predictor
from .datafeeder import SimpleFeeder


class PredictPlugin(DependencyModule):
    __module_name__ = 'predictplugin'

    def on_register_app(self, app):
        pass

    def create(self, **kwargs):
        return Predictor(**kwargs)


class FeederPlugin(DependencyModule):
    __module_name__ = 'feederplugin'

    def on_register_app(self, app):
        pass

    def create(self, type=None, **kwargs):
        return SimpleFeeder(**kwargs)
