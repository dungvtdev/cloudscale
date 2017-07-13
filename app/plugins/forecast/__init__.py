from core import DependencyModule
from .predict import Predictor
from .datafeeder import SimpleFeeder
from .periodicity_detect import period_detect


class PredictPlugin(DependencyModule):
    __module_name__ = 'predictplugin'

    def on_register_app(self, app):
        pass

    def create(self, **kwargs):
        return Predictor(**kwargs)

    @classmethod
    def period_detect(self, series, config):
        return period_detect(series, **config)


class FeederPlugin(DependencyModule):
    __module_name__ = 'feederplugin'

    def on_register_app(self, app):
        pass

    def create(self, type=None, **kwargs):
        return SimpleFeeder(**kwargs)
