from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, String, \
    Integer, Boolean, DateTime, Text
from sqlalchemy.orm import relationship

from app import current_app

Base = current_app.sqlbackend.get_base()


class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True)
    group_id = Column(String(250), nullable=False, unique=True)
    user_id = Column(String(250), nullable=False)
    name = Column(String(250), nullable=False)
    desc = Column(String(250), nullable=True)
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

    instances = relationship("Instance", backref='group')

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
    db_name = Column(String(20))

    group_id = Column(Integer, ForeignKey('group.group_id'))

    def __repr__(self):
        return "<Instance(user_id='%s', instance_id='%s', group_id='%s')>" \
               % (self.user_id, self.instance_id, self.group_id)
