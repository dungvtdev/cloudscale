from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, String, \
    Integer, Boolean, DateTime, Text
from sqlalchemy.orm import relationship, backref

import datetime

from plugins.sqlbackend import Base


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    group_id = Column(String(250), nullable=False, unique=True)
    user_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    desc = Column(String(250))
    image = Column(String(250))
    flavor = Column(String(250))
    selfservice = Column(String(250))
    provider = Column(String(250))
    script_data = Column(Text)
    created = Column(DateTime, default=datetime.datetime.utcnow)

    data_length = Column(Integer)
    recent_point = Column(Integer)
    periodic_number = Column(Integer)
    update_in_time = Column(Integer)

    instances = relationship(
        "Instance", backref=backref('group', lazy='joined'))

    attrs = ['id', 'group_id', 'user_id', 'name', 'desc', 'image', 'flavor',
             'selfservice', 'provider', 'script_data', 'created', 'data_length',
             'recent_point', 'periodic_number', 'update_in_time']

    def parse_dict(self, group_dict):
        for k, v in group_dict.items():
            if k in self.attrs:
                setattr(self, k, v)

    def to_dict(self):
        d = {}
        for k in self.attrs:
            d[k] = getattr(self, k)
        return d

    def __repr__(self):
        return "<User(name='%s')>" \
               % (self.name)


class Instance(Base):
    __tablename__ = 'instance'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(250), nullable=False)
    instance_id = Column(String(250), nullable=False, unique=True)
    endpoint = Column(String(20))
    is_monitoring = Column(Boolean)
    # db_name = Column(String(20))

    group_id = Column(Integer, ForeignKey('group.group_id'))

    attrs = ['id', 'user_id', 'instance_id', 'endpoint', 'is_monitoring',
             'group_id', ]
    #  'db_name']

    def parse_dict(self, vm_dict):
        for k, v in vm_dict.items():
            if k in self.attrs:
                setattr(self, k, v)

    def to_dict(self):
        d = {}
        for k in self.attrs:
            d[k] = getattr(self, k)

        return d

    def __repr__(self):
        return "<Instance(user_id='%s', instance_id='%s', group_id='%s')>" \
               % (self.user_id, self.instance_id, self.group_id)
