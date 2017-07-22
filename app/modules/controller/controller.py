from core import DependencyModule
from core.exceptions import ActionInvalidException, ActionErrorException, \
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
            groupctrl = GroupController(self._app, group_dict, self.on_group_kill)
            self.group_ctrls.add(groupctrl)
            groupctrl.init_group()
            groupctrl.run_up()
        except BaseWrapperException as e:
            raise ActionErrorException(e)

    def on_group_kill(self, group):
        self.group_ctrls.remove(group)

    def update_group(self, group_dict):
        # sua group, update cac param nhung khong duoc update vm
        old_group = self.group.db_get_group(group_dict)
        old_instances = old_group['instances']
        group_dict['instances'] = [[o['instance_id'], o['endpoint']] for o in old_instances]
        # old_group va group_dict da co cung group_id
        # self.group.db_drop_group(old_group)
        self.group.db_create_group(group_dict)

    def drop_group(self, group_dict):
        # group dict dau vao la id
        # xoa group
        group_data = self.group.db_get_group(group_dict)
        if group_data:
            # stop group
            group = self.group_ctrls.get(group_data)
            if group:
                group.shutdown()
        self.group.db_drop_group(group_dict)

    """ ***************************** helper methods *****************************
    ***************************************************************************
    """

    def get_running_group(self, group_dict):
        g = self.group_ctrls.get(group_dict)
        return g

    def is_group_exists(self, group_dict):
        return self.group_ctrls.is_exist(group_dict)
