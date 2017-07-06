from plugins.sqlbackend import dbsession_method
from . import models


class GroupUtils():
    group_params_key = 'group'
    vm_params_key = 'vm'

    def init_app(self, app):
        self._app = app
        app.grouputils = self

    # add or update if group exists
    @dbsession_method
    def db_create_group(self, session, group_dict):
        infomanager = getattr(self._app, 'infomanager')
        if infomanager:
            group_dict = self._app.infomanager.patch_info(
                self.group_params_key, group_dict)

            exists_group = self.dbutils_get_group(
                session, group_dict=group_dict)
            if exists_group:
                exists_group.parse_dict(group_dict)
            else:
                group = models.Group()
                group.parse_dict(group_dict)
                session.add(group)

            session.commit()

    @dbsession_method
    def db_drop_group(self, session, group_dict):
        group = self.dbutils_get_group(session, group_dict=group_dict)
        if group:
            session.delete(group)
            session.commit()

    @dbsession_method
    def db_drop_vm(self, session, vm_dict):
        self.utils_drop_vm(session, vm_dict)
        session.commit()

    @dbsession_method
    def db_create_vm(self, session, vm_dict):
        self.dbutils_create_vm(session, vm_dict)
        session.commit()

    def dbutils_drop_vm(self, session, vm_dict):
        vm = self.dbutils_get_vm(session, vm_dict=vm_dict)
        if vm:
            session.delete(vm)

    def dbutils_create_vm(self, session, vm_dict):
        infomanager = getattr(self._app, 'infomanager')
        if infomanager:
            vm_dict = self._app.infomanager.patch_info(
                self.vm_params_key, vm_dict)

            exists_vm = self.dbutils_get_vm(
                session, vm_dict=vm_dict)
            if exists_vm:
                exists_vm.parse_dict(vm_dict)
            else:
                vm = models.Instance()
                vm.parse_dict(vm_dict)
                session.add(vm)

    def dbutils_get_vm(self, session, id=None, instance_id=None, vm_dict=None):
        if vm_dict and not id and not instance_id:
            return self.dbutils_get_vm(session, id=vm_dict.get('id', None),
                                       instance_id=vm_dict.get('instance_id', None))

        if id:
            instance = session.query(models.Instance).filter(
                models.Instance.id == id).first()
            return instance
        elif instance_id:
            instance = session.query(models.Instance).filter(
                models.Instance.instance_id == instance_id).first()
            return instance

    def dbutils_get_group(self, session, id=None, group_id=None, group_dict=None):
        if group_dict and not id and not group_id:
            return self.dbutils_get_group(session, id=group_dict.get('id', None),
                                          group_id=group_dict.get('group_id', None))

        if id:
            group = session.query(models.Group).filter(
                models.Group.id == id).first()
            return group
        elif group_id:
            group = session.query(models.Group).filter(
                models.Group.group_id == group_id).first()
            return group
