class DefaultParams():
    def init_app(self, app):
        DEFAULT_PARAMS = app.config.get('DEFAULT_PARAMS', {})
        self._default = DEFAULT_PARAMS

    def populate_default_params(self, key, dict_obj):
        default = self._default.get(key, None)
        if default:
            for k, v in default.items():
                dict_obj.setdefault(k, v)
        return dict_obj
