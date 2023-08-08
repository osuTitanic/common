
from sqlalchemy.orm  import sessionmaker, Session
from sqlalchemy      import create_engine
from contextlib      import contextmanager

from .objects import Base

import logging

class Postgres:
    def __init__(self, username: str, password: str, host: str, port: int) -> None:
        self.engine = create_engine(
            f'postgresql://{username}:{password}@{host}:{port}/{username}',
            max_overflow=30,
            pool_recycle=3600,
            pool_size=5,
            echo_pool=None,
            echo=None
        )

        Base.metadata.create_all(bind=self.engine)

        self.logger = logging.getLogger('postgres')
        self.sessionmaker = sessionmaker(bind=self.engine)

    @property
    def session(self) -> Session:
        return self.sessionmaker()

    @contextmanager
    def managed_session(self):
        session = self.sessionmaker()
        try:
            yield session
        except Exception as e:
            self.logger.fatal(f'Transaction failed: {e}')
            self.logger.fatal('Performing rollback...')
            session.rollback()
        finally:
            self.logger.debug('Closing session...')
            session.close()
