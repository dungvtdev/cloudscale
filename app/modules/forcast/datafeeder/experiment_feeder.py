from . import base
import pandas as pd
import numpy as np


def normalize(data):
    return (data - data.min()) / (data.max() - data.min())


def unnormalize(data, minval, maxval):
    return data * (maxval - minval) + minval


def clamp01(data):
    data[(data > 1) | (data < 0)] = np.nan
    data = data.interpolate()
    i = 0
    while (np.isnan(data[i])):
        data[i] = 0
        i = i + 1
    return data


class ExperimentFeeder(base.BaseFeeder):
    def preprocess_data(self, data):
        return normalize(data)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (40*period, 46*period)
        return self.generate(data, range_train)


class ExperimentTestFeeder(base.BaseFeeder):
    def preprocess_data(self, data):
        self._max_val = data.max()
        self._min_val = data.min()
        return normalize(data)

    def postprocess_data(self, data):
        return unnormalize(data, self._min_val, self._max_val)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        range_train = (46*period, 48*period)
        return self.generate(data, range_train)


class ExperimentFeeder2(ExperimentFeeder):
    def preprocess_data(self, data):
        data = clamp01(data)
        return ExperimentFeeder.preprocess_data(self, data)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        period = 480
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        begin = int(1 * period)
        end = int(4.5 * period)
        range_train = (begin, end)
        gdata_x, gdata_y = self.generate(data, range_train)
        # cdata = pd.Series(data=gdata_y)
        # cdata.to_csv('gdata_y', index=False, header=False)
        return gdata_x, gdata_y


class ExperimentTestFeeder2(ExperimentTestFeeder):
    def preprocess_data(self, data):
        data = clamp01(data)
        return ExperimentTestFeeder.preprocess_data(self, data)

    def postprocess_data(self, data):
        return ExperimentTestFeeder.postprocess_data(self, data)

    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        period = 480
        self.setup(n_input=n_input,
                   n_periodic=n_periodic,
                   period=period)
        data = self.data_fetch.fetch_series()
        begin = int(4.5 * period)
        end = int(5 * period)
        range_train = (begin, end)
        return self.generate(data, range_train)
