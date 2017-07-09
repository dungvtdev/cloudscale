from core.exceptions import NotEnoughParams


class GroupController(object):
    def __init__(self, group_dict):
        if not group_dict.get('instances', None):
            raise NotEnoughParams('Create new group must containt vms')
        # tao group
        group_dict = self.group.db_create_group(group_dict)

        # tao cac vm lien quan
        vm_dicts = self.group.db_create_vms_onlynew(group_dict['instances'])

        group_dict['instances'] = vm_dicts

        self.data = group_dict

    def test(self, group_dict):
        return self.data['group_id'] == group_dict['group_id']

    @property
    def vms(self):
        return self.data['instances']

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

    def start(self):
        pass

    def stop(self):
        pass
