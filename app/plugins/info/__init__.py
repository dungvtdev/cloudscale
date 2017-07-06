from .defaultparam import DefaultParams


class InfoManager():
    def __init__(self):
        self._defaultparams = DefaultParams()

    def init_app(self, app):
        self._defaultparams.init_app(app)
        app.infomanager = self

    def get_info(self, key, parent=None):
        if parent is None:
            dict_obj = {}
        else:
            init_info_func = getattr(parent, 'init_info')
            if init_info_func:
                dict_obj = init_info_func(key)

        return self.patch_info(key, dict_obj)

    def patch_info(self, key, dict_obj):
        dict_obj = self._defaultparams.populate_default_params(key, dict_obj)
        return dict_obj


class InfoGetterMixin():
    def init_info(self, key):
        raise NotImplementedError('function init_info must be implement')
