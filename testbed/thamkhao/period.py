import autoperiod as ap
import pandas as pd

# file_name = 'internet-traffic-data-in-bits-fr.csv'
# fs = 240
# threshold=0.08

file_name = 'internet-traffic-data-in-bits-fr (2).csv'
fs = 288
threshold=0.2

data = pd.read_csv(file_name, header=None, skip_footer=4)

data = data[1]

periods = ap.period_detect(data, fs=fs, threshold=threshold)

print(periods)