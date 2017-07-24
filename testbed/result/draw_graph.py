import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime

if __name__ == '__main__':
    ax = plt.subplot()


    file_name = 'cache_2.real.data.csv'

    real_data = pd.read_csv(file_name, header=None)[:500]
    ax.plot(real_data.index, real_data[0], c='red', label='Real')

    file_name = 'cache_2.predict.data.csv'

    predict_data = pd.read_csv(file_name, header=None)[:500]
    ax.plot(predict_data.index, predict_data[0], '--', c='blue', label='predict')

    plt.show()
