from .base import BaseFeeder
from . import exceptions as ex
import pandas as pd


class SimpleFeeder(BaseFeeder):
    def fetch_training(self, n_input=None, n_periodic=None, period=None):
        self.setup(n_input=n_input, n_periodic=n_periodic, period=period)
        data = self.data_fetch.fetch_series()
        past_data_len = n_periodic * period
        if past_data_len > len(data):
            raise ex.NotEnoughData('n_periodic is too big with data len')
        range_train = (past_data_len, len(data))
        return self.generate(data, range_train)

    def preprocess_data(self, data):
        return data
