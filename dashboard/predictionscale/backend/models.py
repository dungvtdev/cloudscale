# import datetime


class GroupData:
    attrs = ['id', 'group_id', 'name', 'desc', 'instances', 'image', 'flavor', 'selfservice',
             'provider', 'script_data', 'created',
             'data_length', 'recent_point', 'periodic_number', 'update_int_time']

    def __init__(self, data_dict):
        # populate attrs
        for k in self.attrs:
            setattr(self, k, None)
        self.parse_dict(data_dict)

    def parse_dict(self, data_dict):
        for k, v in data_dict.items():
            if k in self.attrs:
                setattr(self, k, v)

    def to_dict(self):
        d = {}
        for k in self.attrs:
            d[k] = getattr(self, k)
        return d
