import setup_test
from plugins.forecast import SimpleFeeder
import pandas as pd
import os

data = pd.Series(range(1, 100))
data = data[10:]
k = 1
m = 1
T = 0
p = 4

base_path = os.path.dirname(__file__)
path = os.path.join(base_path, '10min_workload.csv')

# data = pd.read_csv(path, header=None)
# data = data[0]

feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
in_train, out_train = feeder.generate(data, k)
in_test = feeder.generate_train_one(data, k)
print(in_train)
print(out_train)
print(in_test)
