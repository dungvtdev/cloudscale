import datetime


class GroupData:

    def __init__(self, id=None, name=None, group_id=None, desc=None, instances=None,
                 image=None, flavor=None, selfservice=None, provider=None,script_data=None,
                 enable=False, process=None,
                 period=None, data_length=None, recent_point=None,
                 periodic_number=None, predict_length=None,
                 update_in_time=None, neural_size=None, created=None):
        self.id = id
        self.group_id = group_id
        self.name = name
        self.desc = desc
        self.instances = instances
        self.image = image
        self.flavor = flavor
        self.selfservice = selfservice
        self.provider = provider
        self.script_data = script_data
        self.process = process
        enable = enable if enable is not None else False
        self.enable = enable
        self.created = created

        self.period = period
        self.data_length = data_length
        self.recent_point = recent_point
        self.periodic_number = periodic_number
        self.predict_length = predict_length
        self.update_in_time = update_in_time
        self.neural_size = neural_size

        self.instances_id = self.instances
        self.image_id = self.image
        self.flavor_id = self.flavor

        if self.process is None:
            self.process = 'Unknown' if self.enable else 'NotActive'

    def to_dict(self):
        # inst_str = '\n'.join(self.instances)
        return {
            'id': self.id,
            'group_id': self.id,
            'name': self.name,
            'desc': self.desc,
            'instances': self.instances,
            'image': self.image,
            'flavor': self.flavor,
            'selfservice': self.selfservice,
            'provider': self.provider,
            'script_data':self.script_data,
            'enable': self.enable,
            'process': self.process,
            'created': self.created,
            'period': self.period,
            'data_length': self.data_length,
            'recent_point': self.recent_point,
            'periodic_number': self.periodic_number,
            'predict_length': self.predict_length,
            'update_in_time': self.update_in_time,
            'neural_size': self.neural_size,
        }

    @classmethod
    def create(cls, group_dict):
        g = group_dict
        return GroupData(id=g.get('id', None),
                         group_id=g['group_id'],
                         name=g['name'],
                         desc=g['desc'],
                         instances=g['instances'],
                         image=g['image'],
                         flavor=g['flavor'],
                         selfservice=g['selfservice'],
                         provider=g['provider'],
                         script_data=g.get('script_data', ''),
                         enable=g.get('enable', False),
                         process=g.get('process', None),
                         created=g.get('created', None),
                         period=g.get('period', None),
                         data_length=g.get('data_length', None),
                         recent_point=g.get('recent_point', None),
                         periodic_number=g.get('periodic_number', None),
                         predict_length=g.get('predict_length', None),
                         update_in_time=g.get('update_in_time', None),
                         neural_size=g.get('neural_size', None))

    def clone(self):
        return GroupData.create(self.to_dict())
