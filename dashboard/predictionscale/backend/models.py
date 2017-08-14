# import datetime
import copy

class GroupData:
    attrs = ['id', 'group_id', 'name', 'desc', 'instances', 'image', 'flavor', 'selfservice',
             'provider', 'script_data', 'created',
             'data_length', 'recent_point', 'periodic_number', 'update_in_time',
             'proxy_url', 'max_scale_vm', 'number_vm', 'process']

    def __init__(self, data_dict):
        # populate attrs
        for k in self.attrs:
            setattr(self, k, None)
        self.parse_dict(data_dict or {})

    def parse_dict(self, data_dict):
        for k, v in data_dict.items():
            if k in self.attrs:
                setattr(self, k, v)
        # print(data_dict)

    def to_dict(self):
        d = {}
        for k in self.attrs:
            d[k] = getattr(self, k)
        return d

    def clone(self):
        cl = copy.copy(self)
        cl.instances = [copy.copy(i) for i in cl.instances]
        return cl
