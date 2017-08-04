import pandas as pd
import numpy as np
from core import seriesutils as su

"""
** generate function
**** Input: data (list or dataframe 1 chieu), k
**** Output: tap train

** 
"""


class BaseFeeder():
    def __init__(self, **kwargs):
        self.setup(**kwargs)
        self.last_dmin = self.last_dmax = None

    def setup(self, n_input=None, n_periodic=None, period=None):
        self.n_input = n_input
        self.n_periodic = n_periodic
        self.period = period

        if self.period == 0:
            self.n_periodic = 0

    def generate(self, data, k=None, dmin=None, dmax=None):
        # data = self.preprocess_data(data)

        if isinstance(data, list):
            data = pd.DataFrame(data)[0]
        elif isinstance(data, np.ndarray):
            data = pd.DataFrame(data)[0]

        data, dmin, dmax = su.normalize(data, dmin=dmin, dmax=dmax)

        check = pd.DataFrame(data)
        check[check > 1] = np.nan
        print('Is > 1 %s' % check.isnull().any())
        # calc output train range
        # t_start = max(m.T - k, p - 1)
        # o_start = t_start + k
        # o_end = n - k - 1
        t_start = self.period * self.n_periodic - k
        if t_start < self.n_input - 1:
            t_start = self.n_input - 1
        o_start = t_start + k
        o_end = len(data) - k - 1
        output_train = data[o_start:o_end + 1]

        input_train = self.get_train_data(data, output_train=output_train, k=k)

        # output_train = self.normalize(output_train)

        return np.asarray(input_train), np.asarray(output_train), dmin, dmax

    def generate_train_one(self, data, k=0, dmin=None, dmax=None):
        if isinstance(data, list):
            data = pd.DataFrame(data)[0]

        input_train = self.get_train_data(data, k=k)[0]
        input_train, _, _ = su.normalize(input_train, dmin, dmax)
        return np.asarray(input_train)

    def get_train_data(self, raw_data, output_train=None, k=None):
        training = []
        k = k or 1

        # truong hop raw_data bao gom ca input, output cua tap train
        if output_train is not None:
            t_start = output_train.index[0] - k
            t_end = output_train.index[-1] - k
        else:
            # truong hop lay 1 diem cuoi cung, raw_data chi gom input cua tap
            # test
            t_start = len(raw_data) - 1
            t_end = t_start
        for t in range(t_start, t_end + 1):
            temp = []
            for p in range(0, self.n_input):
                temp.append(raw_data[t - p])
            for m in range(1, self.n_periodic + 1):
                pval = raw_data[t - self.n_periodic * self.period + k]
                temp.append(pval)
            training.append(temp)
        return training

        # def generate_extend(self, data, extend):
        #     # idxs = list(range(0, self.n_input))
        #     idxs = []
        #     for m in range(1, self.n_periodic + 1):
        #         idxs.append(m * self.period)

        #     n_d = len(data)
        #     rl = [data[n_d - i - 1] for i in range(0, self.n_input)]
        #     n_ex = len(extend)
        #     for idx in idxs:
        #         if idx >= n_ex:
        #             rl.append(data[n_d - (idx - n_ex) - 1])
        #         else:
        #             rl.append(extend[-idx - 1])
        #     return rl


class SimpleFeeder(BaseFeeder):
    pass
