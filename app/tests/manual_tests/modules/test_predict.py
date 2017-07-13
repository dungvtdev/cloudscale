import setup_test
from modules.forcast import SimpleFeeder, Predictor

data = [1.0 / i for i in range(1, 100)]
k = 3
m = 1
T = 10
p = 4

feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
in_train, out_train = feeder.generate(data, k)

d = {
    'recent_point': p,
    'periodic_number': m,
    'period': T,
    'neural_size': 15
}
predictor = Predictor(**d)
predictor.train(in_train, out_train)

out_test = feeder.generate_train_one(data, k)
pr = predictor.predict_one(out_test)
print(pr)
