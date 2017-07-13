from ..estimators.GAEstimator import GAEstimator
from ..estimators.NeuralFlow import NeuralFlowRegressor
import pandas as pd


class Predictor():
    neural = None

    def __init__(self, recent_point=0, periodic_number=0, period=0, neural_size=0,
                 cross_rate=0.6, mutation_rate=0.04, pop_size=50):
        self._recent_point = recent_point
        self._periodic_number = periodic_number
        self._n_hidden = neural_size
        self._cross_rate = cross_rate
        self._mutation_rate = mutation_rate
        self._pop_size = pop_size
        self.period = period

    def train(self, dataFeeder):
        in_train, out_train = dataFeeder.fetch_training(
            self._recent_point, self._periodic_number, self.period)

        gaEstimator = GAEstimator(cross_rate=self._cross_rate,
                                  mutation_rate=self._mutation_rate,
                                  pop_size=self._pop_size)

        neural_shape = [self._recent_point + self._periodic_number, self._n_hidden, 1]
        fit_param = {
            "neural_shape": neural_shape
        }
        # return in_train, out_train
        gaEstimator.fit(in_train, out_train, **fit_param)
        fit_param["weights_matrix"] = gaEstimator.best_archive
        neuralNet = NeuralFlowRegressor()
        neuralNet.fit(in_train, out_train, **fit_param)
        self.neural = neuralNet

    def predict_test(self, dataFeeder):
        in_test, out_test = dataFeeder.fetch_training(
            self._recent_point, self._periodic_number, self.period)

        out_pred = self.neural.predict(in_test)
        return out_pred, out_test

    def predict(self, data):
        df = pd.DataFrame([data, ])
        return self.neural.predict(df)
