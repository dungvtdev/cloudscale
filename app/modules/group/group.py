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

    def patch_group(self, group_dict):
        infomanager = self.infomanager
        if infomanager:
            group_dict = infomanager.patch_info(
                self.group_params_key, group_dict)
        return group_dict

    def patch_vm(self, vm_dict):
        infomanager = getattr(self._app, 'infomanager')
        if infomanager:
            vm_dict = self._app.infomanager.patch_info(
                self.vm_params_key, vm_dict)
        return vm_dict

    @dbsession_method
    def db_create_group(self, session, group_dict):
        group_dict = self.patch_group(group_dict)

        group_dict.setdefault('group_id', str(uuid.uuid4()))

        exists_group = self.dbutils_get_group_model(
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

        # return group_dict = group_dict_input append default info
        return group_dict

    @dbsession_method
    def db_get_group(self, session, group_dict):
        group = self.dbutils_get_group_model(session, group_dict=group_dict)
        return group.to_dict()

    @dbsession_method
    def db_drop_group(self, session, group_dict):
        group = self.dbutils_get_group_model(session, group_dict=group_dict)
        if group:
            # drop all vm
            for inst in group.instances:
                session.delete(inst)

            session.delete(group)
            session.commit()

    @dbsession_method
    def db_drop_vm(self, session, vm_dict):
        self.dbutils_drop_vm_model(session, vm_dict=vm_dict)
        session.commit()

    @dbsession_method
    def db_create_vm(self, session, vm_dict):
        vm_dict = self.dbutils_create_vm_model(session, vm_dict)
        session.commit()

        return vm_dict

    @dbsession_method
    def db_update_vm(self, session, vm_dict):
        vm = self.dbutils_get_vm_model(vm_dict=vm_dict)
        vm.parse_dict(vm_dict)
        session.commit()

    @dbsession_method
    def db_create_vms_onlynew(self, session, vm_dicts):
        if vm_dicts:
            rl = []
            for vm_dict in vm_dicts:
                vm = self.dbutils_get_vm_model(session, vm_dict=vm_dict)
                if vm:
                    raise ExistsException('VM is exists.')

            for vm_dict in vm_dicts:
                vm_rl = self.dbutils_create_vm_model(session, vm_dict)
                rl.append(vm_rl)

            return rl

    def dbutils_drop_vm_model(self, session, vm_dict):
        vm = self.dbutils_get_vm_model(session, vm_dict=vm_dict)
        if vm:
            session.delete(vm)

    def dbutils_create_vm_model(self, session, vm_dict):
        vm_dict = self.patch_vm(vm_dict)

        exists_vm = self.dbutils_get_vm_model(
            session, vm_dict=vm_dict)
        if exists_vm:
            exists_vm.parse_dict(vm_dict)
        else:
            vm = models.Instance()
            vm.parse_dict(vm_dict)
            session.add(vm)

        # vm_dict is already patched by info
        return vm_dict

    def dbutils_get_vm_model(self, session, id=None, instance_id=None, vm_dict=None):
        if vm_dict and not id and not instance_id:
            return self.dbutils_get_vm_model(session, id=vm_dict.get('id', None),
                                             instance_id=vm_dict.get('instance_id', None))

        if id:
            instance = session.query(models.Instance).filter(
                models.Instance.id == id).first()
            return instance
        elif instance_id:
            instance = session.query(models.Instance).filter(
                models.Instance.instance_id == instance_id).first()
            return instance

    def dbutils_get_group_model(self, session, id=None, group_id=None, group_dict=None):
        if group_dict and not id and not group_id:
            return self.dbutils_get_group_model(session, id=group_dict.get('id', None),
                                                group_id=group_dict.get('group_id', None))

        if id:
            group = session.query(models.Group).filter(
                models.Group.id == id).first()
            return group
        elif group_id:
            group = session.query(models.Group).filter(
                models.Group.group_id == group_id).first()
            return group
