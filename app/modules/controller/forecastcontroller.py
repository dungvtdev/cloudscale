class ForecastCpuController(object):
    def __init__(self, feeder_factory, predict_factory, config=None):
        self.feeder_factory = feeder_factory
        self.predict_factory = predict_factory
        self.config = config

    def train(self, data):
        pass

    def add_last_point(self, value, time):
        pass

    def predict(self):
        pass


class ForecastModule(DependencyModule):
    __module_name__ = 'forecastmodule'

    map_cls = {
        'cpu_usage_total': ForecastCpuController
    }

    def on_register_app(self, app):
        config = {
            'threshold': 0.1,
            'fs': 144
        }
        self.config = app.config.get('FORECAST', config)

    def create_controller(self, **kwargs):
        metric = kwargs['metric']
        ctrl_class = self.map_cls[metric]
        feeder_factory = getattr(self._app, self.config['feeder_factory'])
        predict_factory = getattr(self._app, self.config['predict_factory'])
        return ctrl_class(feeder_factory=feeder_factory,
                          predict_factory=predict_factory,
                          **kwargs)
