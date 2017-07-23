import threading
import time

from core import DependencyModule
from . import OSClient


class OpsVmService(DependencyModule):
    __module_name__ = 'opsvm'

    def on_register_app(self, app):
        app.vmservice = self
        self.osclient = OSClient(app.config['OPS_ACCOUNT'])

    def make_createvm_thread(self, data):
        vmthread = VmCreaterThread(data, self.osclient)
        return vmthread

    def make_dropvm_thread(self, data):
        vmthread = VmDropThread(data, self.osclient)
        return vmthread

    def remove_instances(self, instance_id):
        self.osclient.delete(instance_id)



class VmScaleBaseThread(threading.Thread):
    # state = processing, fail, success
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False

        self.save_exception = None
        self.save_state = None

    def is_finish(self):
        return self.save_state in ['fail', 'success']

    @property
    def exception(self):
        return self.save_exception

    @property
    def state(self):
        return self.save_state


class VmCreaterThread(VmScaleBaseThread):
    CHECK_INTERVAL = 1
    TIME_OUT = 30

    def __init__(self, data, osclient):
        VmScaleBaseThread.__init__(self, data, osclient)

        self.data = data
        self.osclient = osclient

        self._vm = None      # {'instance_id', 'ip'}
        self.save_state = 'none'

    @property
    def vm(self):
        return self._vm

    def run(self):
        try:
            name = self.data['name']
            image_id = self.data['image']
            flavor_id = self.data['flavor']
            net_selfservice_id = self.data['selfservice']
            provider_name = self.data['provider']
            user_data = self.data['user_data']

            self.save_state = 'processing'

            self._vm = self.osclient.create_new_instance(name=name, image_id=image_id,
                                                         flavor_id=flavor_id,
                                                         net_selfservice_id=net_selfservice_id,
                                                         provider_name=provider_name,
                                                         user_data=user_data,
                                                         time_out=self.TIME_OUT,
                                                         check_interval=self.CHECK_INTERVAL)
            self.save_state = 'success'
        except Exception as e:
            self.save_exception = e
            self.save_state = 'fail'


class VmDropThread(VmScaleBaseThread):
    def __init__(self, data, osclient):
        VmScaleBaseThread.__init__(self, data)
        self.data = data
        self.osclient = osclient

    def run(self):
        self.osclient.delete(self.data['instance_id'])
        self.save_state = 'success'
