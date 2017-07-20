from core import DependencyModule
from core.exceptions import ActionInvalidException, ActionErrorException,\
    BaseWrapperException
from core import TSList
from . import GroupController


def compare_groupctrl(g1, g2):
    if not isinstance(g1, GroupController):
        return False
    g2_dict = g2 if isinstance(g2, dict) else g2.data
    return g1.test(g2_dict)


class Controller(DependencyModule):
    __module_name__ = 'controller'

    def __init__(self):
        self.group_ctrls = TSList(compare_groupctrl)

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
            raise ActionInvalidException('Can\'t create a exists group')

        try:
            groupctrl = GroupController(self._app, group_dict)
            self.group_ctrls.add(groupctrl)
            groupctrl.init_group()
            groupctrl.run_up()
        except BaseWrapperException as e:
            raise ActionErrorException(e)

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

    def get_running_group(self, group_dict):
        g = self.group_ctrls.get(group_dict)
        return g

    def is_group_exists(self, group_dict):
        return self.group_ctrls.is_exist(group_dict)
