class App():
    def __init__(self):
        self._config = {}

    def config_from_module(self, config_module):
        # get all upcase attribute
        config = {}
        for key in dir(config_module):
            if key.isupper():
                config[key] = getattr(config_module, key)
        self._config = config

    @property
    def config(self):
        return self._config