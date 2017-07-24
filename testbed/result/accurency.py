from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.utils import check_array

import pandas as pd
import numpy as np
from math import sqrt


def mean_absolute_percentage_error(y_true, y_pred):
    y_true = check_array(y_true)
    y_pred = check_array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true))


file_name = 'cache_2.real.data.csv'
real_data = pd.read_csv(file_name, header=None)[:400]

file_name = 'cache_2.predict.data.csv'
predict_data = pd.read_csv(file_name, header=None)[:400]

mae = mean_absolute_error(real_data, predict_data)
mse = mean_squared_error(real_data, predict_data)
rmse = sqrt(mse)
mape = mean_absolute_percentage_error(real_data, predict_data)

print('mae %s' % mae)
# print('mse %s' % mse)
print('rmse %s' % rmse)
print('mape %s' % mape)
