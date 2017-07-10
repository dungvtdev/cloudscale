import thread
import threading

# from threading import Lock
import time
from core.exceptions import NotEnoughParams, ExistsException
from . import MonitorController


class GroupController(threading.Thread):
    WARM_UP_TIME_SECS = 240

    def __init__(self, app, group_dict):
        threading.Thread.__init__(self)

        self.app = app
        self.logname = group_dict['name']

        self.is_running = False

        self.groupservice = self.app.grouputils

        if not group_dict.get('instances', None):
            raise NotEnoughParams('Create new group must containt vms')
        # tao group
        group_dict = self.groupservice.db_create_group(group_dict)

        # tao cac vm lien quan
        for vm in group_dict['instances']:
            vm['is_monitoring'] = False
            vm['user_id'] = group_dict['user_id']

        try:
            vm_dicts = self.groupservice.db_create_vms_onlynew(
                group_dict['instances'])
        except ExistsException as e:
            # xoa group da tao
            self.groupservice.db_drop_group(group_dict)
            raise e

        group_dict['instances'] = vm_dicts

        self.monitorcontroller = None

        # co thread scale anh huong toi self.data, self._last_scale_time,
        # nhung dong bo la khong can thiet vi khong can duyet self.data va
        # self._last_scale_time chi luu thoi diem cuoi cung scale
        self.data = group_dict

        self._last_scale_time = 0
        # khong dung Boolean vi co the co nhieu thread cung chay, thuc ra
        # khong can dong bo nhung van la giai phap an toan
        self._scaling_threads = []

        self.interval_minute = group_dict['interval_minute']

    def init_group(self):
        # chon 1 vm bat ky lam key de monitor
        self.enable_monitor_vm()

    def test(self, group_dict):
        return self.data['group_id'] == group_dict['group_id']

    @property
    def vms(self):
        return self.data['instances']

    @property
    def opsvm(self):
        return self.app.opsvm

    @property
    def log(self):
        return self.app.logger

    """ Task region
    """

    def enable_monitor_vm(self):
        vm = self.data['instances'][0]
        vm['is_monitoring'] = True
        self.groupservice.db_update_vm(vm)
        self.monitorcontroller = self.create_monitorcontroller(vm)

    def create_monitorcontroller(self, vm):
        group_config = {
            'endpoint': vm['endpoint'],
            'to_db': 'monitor_%s' % self.data['name'],
            'metric': self.data['metric'],
            'interval_minute': self.data['interval_minute'],
        }
        return MonitorController(group_config, self.app)

    """ Status region
    """

    def _get_collect_data_process(self):
        return {
            'name': 'collect',
            'data': {
                'interval': 'inverval',
                'accum': 'accum',
                'vmName': 'vm_name',
            }
        }

    def _get_training_data_process(self):
        return {
            'name': 'training',
            'data': {
                'interval': 'interval',
                'accum': 'accum',
                'vmName': 'vm_name',
                'lastTotalData': 'last_total_data'
            }
        }

    def _get_predict_data_process(self):
        return {
            'name': 'predict',
            'data': {
                'interval': 'interval',
                'accum': 'accum',
                'lastPredict': [],
                'vmName': 'vm_name'
            }
        }

    def _get_scale_process(self):
        return {
            'name': 'scale',
            'data': {
                'accumUp': 'accum_up',
                'accumDown': 'accum_down',
                'nVm': 'n_vm'
            }
        }

    def get_process_info_dict(self):
        # s = {
        #     'processes':[
        #         {
        #             'name': '',
        #             'data':{},
        #         }
        #     ]
        # }
        s = {
            'processes': [
                self._get_collect_data_process(),
                self._get_training_data_process(),
                self._get_predict_data_process(),
                self._get_scale_process()
            ]
        }
        return s

    """ VM regions
    """

    def scale_up(self):
        vm_name_ex = str(uuid.uuid4())[:8]
        name = "%s.%s" % (self.data['name'], vm_name_ex)

        data = {
            'name': name,
            'image': self.data['image'],
            'flavor': self.data['flavor'],
            'selfservice': self.data['selfservice'],
            'provider_name': self.data['provider'],
            'user_data': self.data['user_data'],
        }

        vmthread = self.opsvm.make_createvm_thread(data)

        self._scaling_threads.append(vmthread)
        thread.start_new_thread(self._scale_up_thread, (vmthread, ))

    def _scale_up_thread(self, vmthread):
        vmthread.start()
        vmthread.join()

        self._scaling_threads.remove(vmthread)

        if vmthread.status == 'success':
            self._last_scale_time = time.time()
            vm = vmthread.vm
            vm_dict = {
                'instance_id': vm['instance_id'],
                'endpoint': 'ip',
                'user_id': self.data['user_id'],
                'is_monitoring': False
            }
            vm_dict = self.groupservice.db_create_vm(vm_dict)

            self.data['instances'].append(vm_dict)

            self.log.info('success scale new vm id=%s' % vm['instance_id'])

        if vmthread.status == 'fail':
            self.log.error('fail to scale new vm')

    def scale_down(self):
        # tu chon ra 1 vm khong monitor de xoa
        vm = next((v for v in self.data['instances']
                   if not v['is_monitoring']), None)
        if not vm:
            self.log.error('Logic Error, khong tim thay vm de scale down')
        else:
            vmthread = self.opsvm.make_dropvm_thread(vm)

            self._scaling_threads.append(vmthread)
            thread.start_new_thread(self._scale_down_thread, (vmthread, ))

    def _scale_down_thread(self, vmthread):
        vmthread.start()
        vmthread.stop()

        self._scaling_threads.remove(vmthread)

        if vmthread.status == 'success':
            self._last_scale_time = time.time()

            self.data['instances'].remove(vmthread.data)

            self.log.info('success scale down vm id=%s' %
                          vmthread.data['instance_id'])

        if vmthread.status == 'fail':
            self.log.error('fail to scale down vm id=%s' %
                           vmthread.data['instance_id'])

    def run(self):
        self.log.info('Group %s start' % self.logname)

        interval = self.interval_minute
        try:
            result = self.monitorcontroller.init_data()
            interval = result['first_interval']
            # values = self.monitorcontroller.get_data_series()
            print(sum(len(v) for v in values))
        except Exception as e:
            raise e

        while(self.is_running):
            time.sleep(interval * 60)
            interval = self.interval_minute

            timestamp, value = self.monitorcontroller.get_last_one()
            if timestamp:
                self.log.debug('Group %s get success' % self.logname)
            else:
                self.log.debug('Group %s get fail' % self.logname)

        self.log.info('Group %s stop' % self.logname)

    def run_up(self):
        self.is_running = True
        self.start()

    def shutdown(self):
        self.is_running = False
