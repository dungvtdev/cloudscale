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

    def config_from_dict(self, config_dict):
        for k, v in config_dict.items():
            if k.isupper():
                self._config[k] = v

    @property
    def config(self):
        return self._config
