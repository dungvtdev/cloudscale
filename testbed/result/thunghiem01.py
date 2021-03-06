import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.utils import check_array
from math import sqrt
import matplotlib.dates as mdates


def mean_absolute_percentage_error(y_true, y_pred):
    y_true = check_array(y_true)
    y_pred = check_array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true))


if __name__ == '__main__':
    fig, ax = plt.subplots()

    file_name = 'data.v3_2_4.result.csv'
    # file_name = 'data.result.csv'

    data = pd.read_csv(file_name, header=None)

    time = pd.to_datetime(data[0], format='%Y-%m-%d %H:%M:%S')

    real_data = pd.Series(np.asarray(data[1]), index=time)
    real_data = real_data.interpolate()
    predict_data = pd.Series(np.asarray(data[2]), index=time)
    predict_data = predict_data.interpolate()
    scale_up = pd.Series(np.asarray(data[3]), index=time)
    scale_down = pd.Series(np.asarray(data[4]), index=time)

    n = 240
    total = real_data.shape[0]
    print(total)
    maes = []
    rmses = []
    mapes = []
    start = 0
    while start < total:
        r = real_data[start:start + n]
        p = predict_data[start:start + n]
        maes.append(mean_absolute_error(r, p))
        rmses.append(sqrt(mean_squared_error(r, p)))
        mapes.append(mean_absolute_percentage_error(r, p))
        start = start + n

    print('mae %s' % maes)
    print('rmses %s' % rmses)
    print('mapes %s' % mapes)

    # xu ly scale_up, scale_down
    # scale_up = scale_up.shift(-4, 'T')
    for i in scale_up.index:
        if not np.isnan(scale_up[i]):
            scale_up[i] = real_data[i]

    # scale_down = scale_down.shift(-4, 'T')
    for i in scale_down.index:
        if not np.isnan(scale_down[i]):
            scale_down[i] = real_data[i]

    s = 480
    e = 720
    real_data = real_data[s:e]
    predict_data = predict_data[s:e]
    scale_up = scale_up[s:e]
    scale_down = scale_down[s:e]

    ax.plot(real_data.index, real_data, c='red', zorder=1, label='Real')
    ax.plot(predict_data.index, predict_data, '--',
            c='blue', zorder=2, label='Predict')
    ax.scatter(scale_up.index, scale_up, c='black', s=100,
               marker="o", zorder=3, label='Scale Up')
    ax.scatter(scale_down.index, scale_down, c='black', s=100,
               marker="v", zorder=4, label='Scale Down')

    myFmt = mdates.DateFormatter('%H:%M %d/%m')
    ax.xaxis.set_major_formatter(myFmt)
    ax.set_xticks(ax.get_xticks()[::2])
    ax.legend()
    plt.xlabel('Time')
    plt.ylabel('% CPU / 100')

    # fig.autofmt_xdate()

    plt.show()
