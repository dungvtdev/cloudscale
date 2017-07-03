class GroupUtils():
    def init_app(self, app):
        self._app = app
        app.grouputils = self

    def create_group(self, group_dict):
