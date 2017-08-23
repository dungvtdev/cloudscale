from core import DependencyModule
import thread
import uuid
import time
import copy


class ScaleControllerBase(object):
    logger = None
    logname = None

    def __init__(self, group_data, config, app):
        self.app = app
        self.group_data = group_data

        self.max_value = config['max_value']
        self.sum_length = config['sum_length']
        # self.max_scale = config['max_scale']
        self.max_scale = group_data['max_scale_vm']
        self.warm_up_minutes = config['warm_up_minutes']
        # self.app_port = config['port']
        self.app_port = group_data['app_port']
        self.group_port = group_data['port']

        self.max_length = self.sum_length

        self.base_vm_count = len(group_data['instances'])

        self.data = []
        # self.result = {
        #     'state': '',
        #     'data': '',
        #     'error': '',
        #     'type': ''
        # }
        self.running_func = None
        self.last_scale_time = None
        self._instances = []

    @property
    def instances(self):
        return self._instances

    def clear_instances(self):
        self._instances = []

    def log(self, method, message):
        if self.logger is not None:
            getattr(self.logger, method)(message)

    def add_point(self, point, predict):
        self.data.append(point)
        if self.max_length and len(self.data) > self.max_length:
            start = len(self.data) - self.max_length
            self.data = self.data[start:]
        return self.check(self.data, predict)

    def check(self, data, predict):
        raise NotImplementedError('check method must be implement.')

    def get_status(self):
        if self.running_func:
            return self.running_func()

    def receive(self):
        rl = self.get_status()
        if rl is not None and (rl['state'] == 'success' or rl['state'] == 'fail'):
            self.running_func = None
        return rl


class SimpleScaleController(ScaleControllerBase):
    def check(self, data, predict):
        scale_msg = ''

        if predict >= self.max_value:
            # khi scale up phai doi thoi gian warm_up cho lan scale truoc
            if self.last_scale_time:
                wait_enough = time.time() - self.last_scale_time > self.warm_up_minutes * 60
                if not wait_enough:
                    return

            if len(self.instances) >= self.max_scale:
                return
            func = self.scale_up()
            if func:
                self.running_func = func
                scale_msg = 'up'
                # test
                # print('up')
                # self.instances.append('')
        else:
            average = sum(data) * 1.0 / len(data)
            number = self.base_vm_count + len(self.instances)
            total_load = average * number
            total_load_down_max = 0.8 * self.max_value * (number - 1)
            if total_load < total_load_down_max:
                func = self.scale_down()
                if func:
                    self.running_func = func
                    scale_msg = 'down'
                    # test
                    # print('down')

        # return co the scale khong, va trang thai scale
        return scale_msg

    def test_scale_up(self):
        func = self.scale_up()
        if func:
            self.running_func = func

    def test_scale_down(self):
        func = self.scale_down()
        if func:
            self.running_func = func

    def add_server(self, vm_dict):
        ip = vm_dict['endpoint']
        self.app.haproxy.add_server(ip, self.app_port, self.group_port)

    def remove_server(self, vm_dict):
        ip = vm_dict['endpoint']
        self.app.haproxy.remove_server(ip, self.app_port, self.group_port)

    def scale_up(self, group_data=None):
        if self.running_func is not None:
            return

        group_data = group_data or self.group_data
        vm_name_ex = str(uuid.uuid4())[:8]
        name = "%sui%s" % (self.group_data['name'], vm_name_ex)

        try_again = self.app.config['SCALE']['try_scale_when_fail']

        data = {
            'name': name,
            'image': group_data['image'],
            'flavor': group_data['flavor'],
            'selfservice': group_data['selfservice'],
            'provider': group_data['provider'],
            'user_data': group_data.get('user_data', group_data.get('script_data', None)),
            'try_again': try_again
        }

        result = {}

        vmthread = self.app.opsvm.make_createvm_thread(data)

        def run_thread(thrd):
            thrd.start()
            thrd.join()

            if thrd.state == 'success':
                self.last_scale_time = time.time()
                vm = vmthread.vm
                vm_dict = {
                    'instance_id': vm['instance_id'],
                    'endpoint': vm['ip'],
                    'user_id': group_data['user_id'],
                    'is_monitoring': False
                }
                result['vm'] = vm_dict
                # vm_dict = self.groupservice.db_create_vm(vm_dict)
                self.instances.append(vm_dict)
                self.log('info', '%s success scale new vm id=%s' % (self.logname, vm['instance_id']))

                # them endpoint trong haproxy
                self.add_server(vm_dict)

            if thrd.state == 'fail':
                self.log('error', '%s fail to scale new vm' % self.logname)

        thread.start_new_thread(run_thread, (vmthread,))

        def check_status():
            return {
                'state': vmthread.state,
                'error': vmthread.exception,
                'vm': result.get('vm', None),
                'type': 'up',
                'is_finish': vmthread.state == 'success' or vmthread.state == 'fail',
            }

        return check_status

    def scale_down(self):
        if self.running_func is not None:
            return

        if not self.instances:
            return
        vm = self.instances[0]
        vmthread = self.app.opsvm.make_dropvm_thread(vm)

        def run_thread(thrd):
            thrd.start()
            thrd.join()

            if vmthread.state == 'success':
                # khong dinh nghia scale time vi chi scale up moi dinh nghia
                # self.last_scale_time = time.time()

                self.instances.remove(vm)

                # port = self.group_data['port']
                # self.app.haproxy.remove_server(vm['instance_id'], self.app_port, port)
                self.remove_server(vm)

                self.log('info', '%s success scale down vm id=%s' %
                         (self.logname, vm['instance_id']))

            if vmthread.state == 'fail':
                self.log('error', '%s fail to scale down vm id=%s' %
                         (self.logname, vm['instance_id']))

        thread.start_new_thread(run_thread, (vmthread,))

        def check_status():
            return {
                'state': vmthread.state,
                'error': vmthread.exception,
                'vm': vm,
                'type': 'down',
                'is_finish': vmthread.state == 'success' or vmthread.state == 'fail'
            }

        return check_status


class ScaleFactory(DependencyModule):
    __module_name__ = 'scalefactory'
    map = {
        'simple_scale': SimpleScaleController
    }

    def on_register_app(self, app):
        self.app = app

    def create(self, group_data, config):
        # print(config)
        controller_cls = self.map[config['controller']]
        cf = copy.copy(config['config'])
        # cf['max_scale'] = config['max_scale']
        # cf['max_scale'] = group_data['max_scale_vm']
        cf['warm_up_minutes'] = config['warm_up_minutes']
        controller = controller_cls(group_data, cf, self.app)
        return controller
