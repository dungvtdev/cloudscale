from threading import Lock


class TSList(object):
    def __init__(self, test_func):
        self.lock = Lock()
        self.list = []
        self.test_func = test_func

    def clear(self):
        with self.lock:
            self.list = []

    def add(self, it):
        with self.lock:
            self.list.append(it)

    def remove(self, it):
        cit = self.get(it)
        with self.lock:
            if cit:
                self.list.remove(cit)

    def get(self, it):
        with self.lock:
            f = next((i for i in self.list if i == it), None)
            if not f:
                f = next((i for i in self.list if self.test_func(i, it)), None)
            return f

    def is_exist(self, it):
        cit = self.get(it)
        return cit is not None
