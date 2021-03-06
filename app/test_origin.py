import matplotlib.pyplot as plt
from math import sqrt
from prediction.estimators.GAEstimator import GAEstimator
from sklearn.metrics import mean_squared_error

from prediction.data.traffic_feeder import TrafficFeeder
from prediction.estimators.NeuralFlow import NeuralFlowRegressor
from tests.manual_tests.utils.GraphUtil import *
import numpy as np

if __name__ == '__main__':
    np.random.seed(7)

    n_input = 4
    n_periodic = 0
    n_hidden = 15
    neural_shape = [n_input + n_periodic, n_hidden, 1]

    cross_rate = 0.6
    mutation_rate = 0.04
    pop_size = 50

    dataFeeder = TrafficFeeder()
    X_train, y_train = dataFeeder.fetch_traffic_training(n_input, n_periodic, (40, 47))
    X_test, y_test = dataFeeder.fetch_traffic_test(n_input, n_periodic, (48, 50))
    # retrieve = [n_input+1,(X_train,y_train,X_test,y_test)]
    gaEstimator = GAEstimator(cross_rate=cross_rate, mutation_rate=mutation_rate, pop_size=pop_size)
    fit_param = {
        "neural_shape": neural_shape
    }
    gaEstimator.fit(X_train, y_train, **fit_param)
    fit_param["weights_matrix"] = gaEstimator.best_archive
    neuralNet = NeuralFlowRegressor()
    neuralNet.fit(X_train, y_train, **fit_param)
    y_pred = dataFeeder.convert(neuralNet.predict(X_test))
    print "done"
    print sqrt(mean_squared_error(y_pred, y_test))
    plot_figure(y_pred, y_test)
