import thread
# from threading import Lock
import time
from core.exceptions import NotEnoughParams


class GroupController(object):
    WARM_UP_TIME_SECS = 240

    def __init__(self, groupservice, group_dict):
        self.groupservice = groupservice

        if not group_dict.get('instances', None):
            raise NotEnoughParams('Create new group must containt vms')
        # tao group
        group_dict = self.groupservice.db_create_group(group_dict)

        # tao cac vm lien quan
        for vm in group_dict['instances']:
            vm['is_monitoring'] = False

        vm_dicts = self.groupservice.db_create_vms_onlynew(
            group_dict['instances'])

        group_dict['instances'] = vm_dicts

        # chon 1 vm bat ky lam key de monitor
        self.enable_monitor_vm()

        # co thread scale anh huong toi self.data, self._last_scale_time,
        # nhung dong bo la khong can thiet vi khong can duyet self.data va
        # self._last_scale_time chi luu thoi diem cuoi cung scale
        self.data = group_dict

        self._last_scale_time = 0
        # khong dung Boolean vi co the co nhieu thread cung chay, thuc ra
        # khong can dong bo nhung van la giai phap an toan
        self._scaling_threads = []

    def test(self, group_dict):
        return self.data['group_id'] == group_dict['group_id']

    @property
    def vms(self):
        return self.data['instances']

    @property
    def opsvm(self):
        return self._app.opsvm

    @property
    def log(self):
        return self._app.logger

    """ Task region
    """
    def enable_monitor_vm():
        vm = self.data['instances'][0]
        vm['is_monitoring'] = True
        self.groupservice.db_update_vm(vm)

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
            'provider_name': self.data['provider']
            'user_data': self.data['user_data']
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
                'instance_id': vm['instance_id']
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

    def start(self):
        pass

    def stop(self):
        pass
