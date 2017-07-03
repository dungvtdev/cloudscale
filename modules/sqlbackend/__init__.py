from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app import get_current_app


def dbsession(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        app = get_current_app()
        if app:
            session = app.sqlbackend.new_session()
            rl = func(session, *args, **kwargs)
            app.sqlbackend.close_session()
        else:
            raise Exception('App must be init first.')
    return func_wrapper


class SQLBackend():
    def init_app(self, app):
        DB_PATH = app.config.get('DB_PATH', 'sqlite:///db.sqlite')
        self._engine = create_engine(DB_PATH, echo=False)
        self._session = scoped_session(sessionmaker(bind=self._engine))

        app.sqlbackend = self

    def create_all(self, base):
        base.metadata.create_all(self._engine)

    def new_session(self):
        self._session()
        return self._session

    def close_session(self):
        self._session.remove()
