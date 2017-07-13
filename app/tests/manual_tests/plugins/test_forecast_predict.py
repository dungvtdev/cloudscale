import setup_test
from plugins.forecast import SimpleFeeder, Predictor
import pandas as pd
import os
from tests.manual_tests.utils.GraphUtil import plot_figure

base_path = os.path.dirname(__file__)


def test_simple():
    k = 3
    m = 1
    T = 10
    p = 4
    feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
    d = {
        'recent_point': p,
        'periodic_number': m,
        'period': T,
        'neural_size': 15
    }
    predictor = Predictor(**d)

    data = [1.0 / i for i in range(1, 100)]
    in_train, out_train = feeder.generate(data, k)
    predictor.train(in_train, out_train)
    out_test = feeder.generate_train_one(data, k)
    pr = predictor.predict_one(out_test)
    print(pr)


# test_simple()

def test_data():
    k = 1
    m = 1
    T = 142
    p = 4
    feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
    d = {
        'recent_point': p,
        'periodic_number': m,
        'period': T,
        'neural_size': 15
    }
    predictor = Predictor(**d)
    path = os.path.join(base_path, '10min_workload.csv')
    data = pd.read_csv(path, header=None)
    data = data[0]
    dmin = data.min()
    dmax = data.max()
    data = (data - dmin) / (dmax - dmin)

    train = data[142 * 39:142 * 46]
    test = data[142 * 45:142 * 48]

    in_train, out_train = feeder.generate(train, k)
    in_test, out_test = feeder.generate(test, k)

    predictor.train(in_train, out_train)
    out_pred = predictor.predict_test(in_test)

    out_test = out_test * (dmax - dmin) + dmin
    out_pred = out_pred * (dmax - dmin) + dmin

    plot_figure(out_pred, out_test)


test_data()
