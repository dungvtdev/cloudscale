data = pd.DataFrame(data).set_index(data.index / minute_per_one)
data = data.groupby(data.index).mean()[0]

self._max = data.max()
self._min = data.min()
data = (data - self._min) / (self._max - self._min)

def _normalize(self, data):
    if not isinstance(data, list):
        data = (data - self._min) / (self._max - self._min)
    else:
        for i in range(len(data)):
            data[i] = (data[i] - self._min) / (self._max - self._min)
    return data

def _unnormalize(self, data):
    if not isinstance(data, list):
        return data * (self._max - self._min) + self._min
    else:
        for i in range(len(data)):
            data[i] = data[i] * (self._max - self._min) + self._min
        return data