import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime

if __name__ == '__main__':
    ax = plt.subplot()

    file_name = 'real.data.csv'

    real_data = pd.read_csv(file_name, header=None)
    ax.plot(real_data.index, real_data[0], label='Real')

    file_name = 'predict.data.csv'

    predict_data = pd.read_csv(file_name, header=None)
    ax.plot(predict_data.index, predict_data[0], label='predict')

    plt.show()