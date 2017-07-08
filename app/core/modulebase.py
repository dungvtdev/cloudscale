class DependencyModule(object):
    def __init__(self):
        pass

    def init_app(self, app):
        self._app = app
        setattr(app, self.__module_name__, self)
        self.on_register_app(app)

    def on_register_app(self, app):
        raise NotImplementedError('Method on_register_app must be implement')