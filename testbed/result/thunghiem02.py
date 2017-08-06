import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.utils import check_array
from math import sqrt


def mean_absolute_percentage_error(y_true, y_pred):
    y_true = check_array(y_true)
    y_pred = check_array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true))


if __name__ == '__main__':
    ax = plt.subplot()
    begin = '2017-08-02 15:50:00'
    end = '2017-08-03 03:15:00'

    file_name = 'data.result.2_4.2_8.csv'
    file_name_total = 'data.result.2_4.2_8.real.csv'

    data = pd.read_csv(file_name, header=None)

    time = pd.to_datetime(data[0], format='%Y-%m-%d %H:%M:%S')

    real_data = pd.Series(np.asarray(data[1]), index=time)
    real_data = real_data.interpolate()
    predict_data = pd.Series(np.asarray(data[2]), index=time)
    predict_data = predict_data.interpolate()
    scale_up = pd.Series(np.asarray(data[3]), index=time)
    scale_down = pd.Series(np.asarray(data[4]), index=time)

    total_data_raw = pd.read_csv(file_name_total, header=None)
    time_total = pd.to_datetime(total_data_raw[0], format='%Y-%m-%d %H:%M:%S')
    total_data = pd.Series(np.asarray(total_data_raw[1]), index=time_total)

    real_data = real_data.ix[begin: end]
    predict_data = predict_data.ix[begin:end]
    scale_up = scale_up.ix[begin:end]
    scale_down = scale_down.ix[begin:end]
    total_data = total_data.ix[begin:end]

    # ax.plot(total_data.index, total_data, c='green', zorder=0, label='Total')
    ax.fill_between(total_data.index, total_data, color='#cccccc', zorder=-2)

    ax.plot(real_data.index, real_data, c='red', zorder=1, label='Real')
    ax.plot(predict_data.index, predict_data, '--',
            c='blue', zorder=2, label='predict')
    ax.scatter(scale_up.index, scale_up, c='black', s=500,
               marker="o", zorder=-1, label='scalue_up')
    ax.scatter(scale_down.index, scale_down, c='black', s=500,
               marker="v", zorder=-1, label='scale_up')

    plt.show()
