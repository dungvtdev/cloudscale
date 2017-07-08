import uuid

from plugins.sqlbackend import dbsession_method
from . import models
from core import DependencyModule
from core.exceptions import ExistsException


class GroupUtils(DependencyModule):
    __module_name__ = 'grouputils'

    group_params_key = 'group'
    vm_params_key = 'vm'

    def on_register_app(self, app):
        pass

    @property
    def infomanager(self):
        return self._app.infomanager

    @dbsession_method
    def db_create_group(self, session, group_dict):
        infomanager = self.infomanager
        if infomanager:
            group_dict = self._app.infomanager.patch_info(
                self.group_params_key, group_dict)

            group_dict.setdefault('group_id', str(uuid.uuid4()))

            rl_group_id = None

            exists_group = self.dbutils_get_group(
                session, group_dict=group_dict)
            if exists_group:
                exists_group.parse_dict(group_dict)
                rl_group_id = exists_group.group_id
            else:
                group = models.Group()
                group.parse_dict(group_dict)
                session.add(group)
                rl_group_id = group.group_id

            session.commit()

            return rl_group_id

    @dbsession_method
    def db_get_group(self, session, group_dict):
        return self.dbutils_get_group(session, group_dict=group_dict)

    @dbsession_method
    def db_drop_group(self, session, group_dict):
        group = self.dbutils_get_group(session, group_dict=group_dict)
        if group:
            # drop all vm
            for inst in group.instances:
                session.delete(inst)

            session.delete(group)
            session.commit()

    @dbsession_method
    def db_drop_vm(self, session, vm_dict):
        self.dbutils_drop_vm(session, vm_dict=vm_dict)
        session.commit()

    @dbsession_method
    def db_create_vm(self, session, vm_dict):
        self.dbutils_create_vm(session, vm_dict)
        session.commit()

    @dbsession_method
    def db_create_vms_onlynew(self, session, vm_dicts):
        if vm_dicts:
            for vm_dict in vm_dicts:
                vm = self.dbutils_get_vm(session, vm_dict=vm_dict)
                if vm:
                    raise ExistsException('VM is exists.')

            for vm_dict in vm_dicts:
                self.dbutils_create_vm(session, vm_dict)

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
