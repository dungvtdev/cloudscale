class DefaultParams():
    def init_app(self, app):
        DEFAULT_PARAMS = app.config.get('DEFAULT_PARAMS', {})
        self._default = DEFAULT_PARAMS
        self._app = app

    def populate_default_params(self, key, dict_obj):
        default = self._default.get(key, None)
        if default:
            if isinstance(default, list):
                for it in default:
                    df = self._default.get(it, None)
                    if not df:
                        self._app.logger.error(
                            "The default params %s not define" % it)
                    else:
                        for k, v in df.items():
                            dict_obj.setdefault(k, v)
            else:
                for k, v in default.items():
                    dict_obj.setdefault(k, v)
        return dict_obj
