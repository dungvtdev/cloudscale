import setup_test
import pandas as pd
import os
from plugins.forecast.periodicity_detect import period_detect

base_path = os.path.dirname(__file__)
path = os.path.join(base_path, '10min_workload.csv')

data = pd.read_csv(path, header=None)
data = data[0]

pr = period_detect(data, threshold=0.1, fs=144)
print(pr)
