import setup_test
from plugins.forecast import SimpleFeeder, Predictor
import pandas as pd
import numpy as np
import os
from tests.manual_tests.utils.GraphUtil import plot_figure
from sklearn.metrics import mean_absolute_error

base_path = os.path.dirname(__file__)


def test_simple():
    k = 3
    m = 0
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

    data = [1.0 / i for i in range(1, 20000)]
    in_train, out_train = feeder.generate(data, k)
    predictor.train(in_train, out_train)
    out_test = feeder.generate_train_one(data, k)
    pr = predictor.predict_one(out_test)
    print(pr)


# test_simple()


def test_data():
    # np.random.seed(7)

    k = 2
    m = 0
    T = 144
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

    train = data[142 * 45:142 * 52]
    print(train.min())
    print(train.max())
    test = data[142 * 53:142 * 55]
    print(test.min())
    print(test.max())

    dtmin, dtmax = 0, 1796037
    in_train, out_train, dmin, dmax = feeder.generate(train, k=k, dmin=dtmin, dmax=dtmax)
    in_test, out_test, dtmin, dtmax = feeder.generate(test, k=k, dmin=dtmin, dmax=dtmax)

    # print(dtmin == dmin and dtmax == dmax)

    out_test = out_test * (dtmax - dtmin) + dtmin

    predictor.train(in_train, out_train, dmin, dmax)
    out_pred = predictor.predict_test(in_test)

    out_pred = out_pred * (dtmax - dtmin) + dtmin

    mae = mean_absolute_error(out_test, out_pred)
    print(mae)
    max_fail = 0
    for i in range(out_test.shape[0]):
        if max_fail < out_test[i] - out_pred[i]:
            max_fail = out_test[i] - out_pred[i]
    print(max_fail)

    print(mean_absolute_error(out_test, out_pred))

    plot_figure(out_pred, out_test)


# test_data()


def test_data2():
    k = 1
    m = 0
    T = 0
    p = 4
    feeder = SimpleFeeder(n_input=p, n_periodic=m, period=T)
    d = {
        'recent_point': p,
        'periodic_number': m,
        'period': T,
        'neural_size': 15,
        'cross_rate': 0.6,
        'mutation_rate': 0.02,
        'pop_size': 50
    }
    predictor = Predictor(**d)
    path = os.path.join(base_path, 'data.full.csv')
    data = pd.read_csv(path, header=None)
    data = data[1]
    # dmin = data.min()
    # dmax = data.max()
    # data = (data - dmin) / (dmax - dmin)

    # train = data[142 * 39:142 * 46]
    # test = data[142 * 45:142 * 48]
    train = data[20:4800]
    test = data[5000:5200]

    in_train, out_train, dmin, dmax = feeder.generate(train, k)
    in_test, out_test, dmin, dmax = feeder.generate(test, k, 0, 1)

    predictor.train(in_train, out_train)
    out_pred = predictor.predict_test(in_test)

    # out_test = out_test * (dmax - dmin) + dmin
    # out_pred = out_pred * (dmax - dmin) + dmin

    plot_figure(out_pred, out_test)


test_data2()
