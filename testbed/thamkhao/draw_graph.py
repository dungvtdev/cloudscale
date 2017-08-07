import requests
import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import datetime

if __name__ == '__main__':
    ax = plt.subplot()


    file_name = 'internet-traffic-data-in-bits-fr (2).csv'

    data = pd.read_csv(file_name, header=None, skip_footer=4)

    time = pd.to_datetime(data[0], format='%Y-%m-%d %H:%M:%S')
    real_data = pd.Series(np.asarray(data[1]), index=time)

    ax.plot(real_data.index, real_data, c='red', label='Real')

    plt.show()
