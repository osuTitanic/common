
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import create_engine, text
from contextlib import contextmanager
from typing import Generator

from ..config import Config
from .. import officer

from .objects import Base
from . import extensions

import logging
import time

class Postgres:
    def __init__(self, config: Config) -> None:
        self.engine = create_engine(
            config.POSTGRES_DSN,
            poolclass=QueuePool if config.POSTGRES_POOL_ENABLED else NullPool,
            max_overflow=config.POSTGRES_POOL_SIZE_OVERFLOW,
            pool_size=config.POSTGRES_POOL_SIZE,
            pool_pre_ping=config.POSTGRES_POOL_PRE_PING,
            pool_recycle=config.POSTGRES_POOL_RECYCLE,
            pool_timeout=config.POSTGRES_POOL_TIMEOUT,
            echo_pool=None,
            echo=None
        )
        self.sessionmaker = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )
        self.ignored_exceptions = (
            'RequestValidationError',
            'HTTPException',
            'Unauthorized',
            'Forbidden',
            'NotFound'
        )
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.logger = logging.getLogger('postgres')

    @property
    def session(self) -> Session:
        return self.sessionmaker(bind=self.engine)

    @contextmanager
    def managed_session(self) -> Generator[Session, None, None]:
        yield from self.yield_session()

    def yield_session(self) -> Generator[Session, None, None]:
        session = self.sessionmaker(bind=self.engine)

        try:
            yield session
        except Exception as e:
            self.log_transaction_failure(e)
            session.rollback()
            raise
        finally:
            session.close()

    def wait_for_connection(self, retries: int = 10, delay: int = 1) -> None:
        for attempt in range(retries):
            try:
                with self.managed_session() as session:
                    session.execute(text('SELECT 1'))
                    return None
            except Exception as e:
                self.logger.warning(f'Failed to connect: "{e}" (attempt {attempt+1}/{retries})')
                time.sleep(delay)

        raise ConnectionError('Failed to establish a connection to the database')
    
    def log_transaction_failure(self, e: Exception) -> None:
        exception_name = e.__class__.__name__

        if exception_name in self.ignored_exceptions:
            return

        self.executor.submit(officer.call, 'Database transaction failed', exc_info=e, exc_offset=1)
        self.logger.warning('Performing rollback...')
