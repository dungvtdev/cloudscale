import pandas as pd
import numpy as np


def clamp01(data):
    data[(data > 1) | (data < 0)] = np.nan
    data = data.interpolate()
    i = 0
    while (np.isnan(data[i])):
        data[i] = 0
        i = i + 1
    return data


class ForecastControllerBase(object):
    def __init__(self, config, app):
        app_config = {
            'threshold': 0.1,
            'fs': 144
        }
        app_config = app.config['FORECAST'] or app_config
        self.feeder_plugin = getattr(app, app_config['feeder_plugin'])
        self.predict_plugin = getattr(app, app_config['predict_plugin'])

        config.setdefault('threshold', app_config['threshold'])
        config.setdefault('fs', app_config['fs'])

        self.config = config
        self.predictor = None
        self.feeder = None
        self.datacache = None
        self.app = app

    def train(self, data):
        if isinstance(data, list):
            data = pd.DataFrame(data)[0]
        elif isinstance(data, np.ndarray):
            data = pd.DataFrame(data)[0]

        del self.predictor
        del self.feeder
        del self.datacache

        pd_params = {
            'threshold': self.config['threshold'],
            'fs': self.config['fs']
        }
        periods = self.predict_plugin.period_detect(data, **pd_params)
        if not periods:
            periodic_number = 0
            period = 0
        else:
            periodic_number = self.config['periodic_number']
            period = int(periods[0] * self.config['fs'])

        fd = {
            'n_input': self.config['recent_point'],
            'n_periodic': periodic_number,
            'period': period
        }

        self.feeder = self.feeder_plugin.create(**fd)

        pd = {
            'recent_point': self.config['recent_point'],
            'periodic_number': periodic_number,
            'period': period,
            'neural_size': 15,
            'cross_rate': self.config['cross_rate'],
            'mutation_rate': self.config['mutation_rate'],
            'pop_size': self.config['pop_size']
        }

        predict_length = self.config['predict_length']

        self.predictor = self.predict_plugin.create(**pd)

        # train data
        in_train, out_train = self.feeder.generate(data, predict_length)
        self.predictor.train(in_train, out_train)

        # cache lai data
        base_length = max(periodic_number * period -
                          predict_length, self.config['recent_point'])
        max_length = int(1.2 * base_length)
        self.datacache = DataLoop(
            max_length, base_length, data[len(data) - base_length:])

    def add_last_point(self, value):
        self.datacache.append(value)

    def predict(self):
        predict_length = self.config['predict_length']
        data = self.datacache.get_valid_data()
        if data is not None:
            out = self.feeder.generate_train_one(data, predict_length)
            pr = self.predictor.predict_one(out)
            return pr


class ForecastCpuController(ForecastControllerBase):
    def __init__(self, config, app):
        ForecastControllerBase.__init__(self, config, app)

    def train(self, data):
        if isinstance(data, list):
            data = pd.DataFrame(data)[0]
        elif isinstance(data, np.ndarray):
            data = pd.DataFrame(data)[0]

        # clamp data [0,1]
        data = clamp01(data)
        return ForecastControllerBase.train(self, data)

    def add_last_point(self, value, time):
        return ForecastControllerBase.add_last_point(self, value, time)

    def predict(self):
        return ForecastControllerBase.predict(self)


class DataLoop(object):
    def __init__(self, max_length, base_length, data):
        self.max_length = max_length
        self.base_length = base_length
        self.data = pd.Series([]).append(data, ignore_index=True)

    def check_length(self):
        len_data = len(self.data)
        if len_data > max_length:
            delta = len_data - max_length
            new_data = pd.Series([]).append(
                self.data[delta:], ignore_index=True)
            del self.data
            self.data = new_data

    def append(self, value):
        need_interpolate = np.isnan(
            self.data[len(self.data) - 1]) and not np.isnan(value)
        self.data.append(pd.Series([value, ]), ignore_index=True)
        if need_interpolate:
            self.data = self.data.interpolate()
        self.check_length()

    def get_valid_data(self):
        is_valid = not np.isnan(self.data[len(self.data) - 1])
        if is_valid:
            return self.data
        return None
