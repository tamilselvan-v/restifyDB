from contextlib import contextmanager

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker


class DBConnection(object):
    """ Place to hold Useful Database Functions"""

    def __init__(self, user, password, db, host, port, dialect="postgresql") -> None:
        """
        Args:
            user:
            password:
            db:
            host:
            port:
        Returns:
        """
        url = f"{dialect}://{user}:{password}@{host}:{port}/{db}"
        # The return value of create_engine() is our connection object
        self.engine = sqlalchemy.create_engine(url)

        # We then bind the connection to MetaData()
        self.meta = MetaData().reflect(bind=self.engine)

        # session maker for creating sessions
        self._session_maker = sessionmaker(bind=self.engine)

    @contextmanager
    def session_scope(self) -> None:
        """Provide a transactional scope around a series of operations"""
        session = self._session_maker(expire_on_commit=False)

        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def create_tables(self, base: object) -> None:
        """Create all tables defined using the given declarative base object"""
        base.metadata.create_all(bind=self.engine)
