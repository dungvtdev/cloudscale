from core import DependencyModule


class HealthCheckController(DependencyModule):
    __module_name__ = 'healthcheck'

    def __init__(self):
        DependencyModule.__init__(self)
        self.reboot_controller = None

    def on_register_app(self, app):
        self.reboot_controller = RebootController(app)

    def reboot_server(self, data):
        return self.reboot_controller.reboot(data)


class RebootController(object):
    def __init__(self, app):
        self.running = {}
        self.opsvm = app.opsvm

    def reboot(self, data):
        instance_id = data['instance_id']
        if instance_id in self.running:
            thrd = self.running[instance_id]['thread']
            if thrd.save_exception:
                raise thrd.save_exception
            if thrd.save_state in ['fail', 'success']:
                del self.running[instance_id]
            return thrd.save_state

        thrd = self.opsvm.make_reboot_thread({'instance_id': instance_id})
        print('This printed message must be only call one per instance_id')
        thrd.start()

        self.running[instance_id] = {
            'thread': thrd
        }

        return thrd.save_state
