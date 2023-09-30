
from sqlalchemy.orm  import sessionmaker, Session
from sqlalchemy      import create_engine
from contextlib      import contextmanager

from .objects import Base

import logging
import config

class Postgres:
    def __init__(self, username: str, password: str, host: str, port: int) -> None:
        self.engine = create_engine(
            f'postgresql://{username}:{password}@{host}:{port}/{username}',
            max_overflow=config.POSTGRES_POOLSIZE_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=900,
            pool_timeout=5,
            pool_size=config.POSTGRES_POOLSIZE,
            echo_pool=None,
            echo=None
        )

        self.engine

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
            self.logger.fatal(f'Transaction failed: {e}', exc_info=e)
            self.logger.fatal('Performing rollback...')
            session.rollback()
        finally:
            session.close()
