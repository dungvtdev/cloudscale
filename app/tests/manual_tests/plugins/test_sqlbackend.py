import setup_test
import os

from bootstrap import app
from plugins import sqlbackend as sql

from sqlalchemy import Column, Integer

# test config
conf = {
    'DB_PATH': 'sqlite:///test.db.sqlite'
}

path = os.path.join(os.path.dirname(__file__), 'test.db.sqlite')

app.config_from_dict(conf)

sqlbackend = sql.SQLBackend()
sqlbackend.init_app(app)


# test model
Base = sqlbackend.get_base()


class TestModel(Base):
    __tablename__ = 'testmodel'

    id = Column(Integer, primary_key=True)
    number = Column(Integer)


app.sqlbackend.create_all()


@sql.dbsession
def test_action(session, i):
    m = TestModel()
    m.number = i
    session.add(m)
    session.commit()


class TestObject():
    @sql.dbsession_method
    def test_action(self, session, i):
        m = TestModel()
        m.number = i
        session.add(m)
        session.commit()


print('Test data, create new database sqlite.')
test_action(10)
t = TestObject()
t.test_action(10)

print('Delete sqlite database')
os.remove(path)
