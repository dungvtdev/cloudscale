from core import DependencyModule
from core.exceptions import InvalidActionException, NotEnoughParams


class Controller(DependencyModule):
    def on_register_app(self, app):
        pass

    @property
    def group(self):
        return self._app.grouputils

    """ ***************************** api methods *****************************
    ***************************************************************************
    """

    def create_group(self, group_dict):
        # khoi tao group moi, neu group da ton tai bao loi
        if self.is_group_exists(group_dict):
            raise InvalidActionException('Can\'t create a exists group')

        if not group_dict.get('instances', None):
            raise NotEnoughParams('Create new group must containt vms')

        # tao group
        self.group.db_create_group(group_dict)

        # tao cac vm lien quan
        self.group.db_create_vms_onlynew(group_dict['instances'])

    def update_group(self, group_dict):
        # sua group, update cac param nhung khong duoc update vm
        group_dict.set_default('instances', None)
        self.group.db_create_group(group_dict)

    def drop_group(self, group_dict):
        # xoa group
        self.group.db_drop_group(group_dict)

    """ ***************************** helper methods *****************************
    ***************************************************************************
    """

    def is_group_exists(self, group_dict):
        return False
