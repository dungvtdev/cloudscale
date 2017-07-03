from .defaultparam import DefaultParams


class InfoManager():
    def __init__(self):
        self._defaultparams = DefaultParams()

    def init_app(self, app):
        self._defaultparams.init_app(app)
        app.infomanager = self

    def get_info(self, key, parent=None):
        if parent is None:
            obj = {}
        else:
            init_info_func = getattr(parent, 'init_info')
            if init_info_func:
                obj = init_info_func(key)

        return self.patch_info(key, obj)

    def patch_info(self, key, obj):
        obj = self._defaultparams.populate_default_params(key, obj)
        return obj


class InfoGetterMixin():
    def init_info(self, key):
        raise NotImplementedError('function init_info must be implement')
