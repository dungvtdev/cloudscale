import matplotlib.pyplot as plt
from math import sqrt
from prediction.estimators.GAEstimator import GAEstimator
from sklearn.metrics import mean_squared_error

from prediction.data.traffic_feeder import TrafficFeeder
from prediction.estimators.NeuralFlow import NeuralFlowRegressor
from tests.manual_tests.utils.GraphUtil import *
import numpy as np
from plugins.forecast.datafeeder import SimpleFeeder

if __name__ == '__main__':
    np.random.seed(7)

    n_input = 4
    n_periodic = 0
    n_hidden = 15
    neural_shape = [n_input + n_periodic, n_hidden, 1]

    cross_rate = 0.6
    mutation_rate = 0.04
    pop_size = 50

    feeder = SimpleFeeder()
    feeder.setup(n_input=n_input, n_periodic=n_periodic, period=142)
    data = pd.Series.from_csv("10min_workload.csv", header=None, index_col=None)
    dmin = data.min()
    dmax = data.max()
    data = (data - dmin) / (dmax - dmin)

    X_train, y_train = feeder.generate(data[40 * 142 - 4:47 * 142], 1)
    X_test, y_test = feeder.generate(data[48 * 142 - 4:50 * 142], 1)

    # dataFeeder = TrafficFeeder()
    # X_train, y_train = dataFeeder.fetch_traffic_training(n_input, n_periodic, (40, 47))
    # X_test, y_test = dataFeeder.fetch_traffic_test(n_input, n_periodic, (48, 50))
    # retrieve = [n_input+1,(X_train,y_train,X_test,y_test)]
    gaEstimator = GAEstimator(cross_rate=cross_rate, mutation_rate=mutation_rate, pop_size=pop_size)
    fit_param = {
        "neural_shape": neural_shape
    }
    gaEstimator.fit(X_train, y_train, **fit_param)
    fit_param["weights_matrix"] = gaEstimator.best_archive
    neuralNet = NeuralFlowRegressor()
    neuralNet.fit(X_train, y_train, **fit_param)
    # y_pred = dataFeeder.convert(neuralNet.predict(X_test))
    y_pred = neuralNet.predict(X_test)
    print "done"
    print sqrt(mean_squared_error(y_pred, y_test))
    plot_figure(y_pred, y_test)
