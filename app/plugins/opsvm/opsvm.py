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


class VmCreaterThread(threading.Thread):
    # state = processing, fail, success
    CHECK_INTERVAL = 1
    TIME_OUT = 30

    def __init__(self, data, osclient):
        threading.Thread.__init__(self)
        self.daemon = False

        self.data = data
        self.osclient = osclient

        self._exception = None
        self._state = None
        self._vm = None      # {'instance_id', 'ip'}

    def is_finish(self):
        return self._state in ['fail', 'success']

    @property
    def exception(self):
        return self._exception

    @property
    def state(self):
        return self._state

    def run(self):
        try:
            name = self.data['name']
            image_id = self.data['image']
            flavor_id = self.data['flavor']
            net_selfservice_id = self.data['selfservice']
            provider_name = self.data['provider_name']
            user_data = self.data['user_data']

            self._state = 'processing'

            self._vm = self.osclient.create_new_instance(name=name, image_id=image_id,
                                                         flavor_id=flavor_id,
                                                         net_selfservice_id=net_selfservice_id,
                                                         provider_name=provider_name,
                                                         user_data=user_data,
                                                         time_out=self.TIME_OUT,
                                                         check_interval=self.CHECK_INTERVAL)
            self._state = 'success'
        except Exception as e:
            self._exception = e
            self._state = 'fail'


class VmDropThread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.data = data
        self.osclient = osclient

        self.state = None
        self.exception = None

    def run(self):
        self.osclient.delete(self.data['instance_id'])
        self.state = 'success'
