import pandas as pd
from matplotlib import pyplot as plt
import numpy as np


if __name__ == '__main__':
    ax = plt.subplot()

    file_name = 'data.v3_2_4.result.csv'

    mae_1 = pd.Series([0.0389492, 0.0337054, 0.03309157])
    mae_2 = pd.Series([0.0441327, 0.0280163, 0.0261925])

    rmse_1 = pd.Series([0.0688761, 0.0667234, 0.0525199])
    rmse_2 = pd.Series([0.0724164, 0.0431355, 0.0369108])

    mape_1 = pd.Series([0.1135399, 0.0983195, 0.0897212])
    mape_2 = pd.Series([0.1390710, 0.0869374, 0.0977987])

    d1 = mape_1
    d2 = mape_2

    ax.plot(d1.index, d1, c='red', zorder=1, label='thunghiem1')
    ax.plot(d2.index, d2, '--',
            c='blue', zorder=2, label='thunghiem2')

    plt.show()
