import setup_test
from modules.forcast import SimpleFeeder, Predictor

data = range(1, 100)
k = 3
m = 1
T = 10
p = 4

feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
in_train, out_train = feeder.generate(data, k)
print(in_train)
print(out_train)
