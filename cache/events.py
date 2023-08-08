
from typing import Dict, Generator, Callable
from redis import Redis

import logging
import time

class EventQueue:
    def __init__(self, name: str, connection: Redis) -> None:
        self.redis = connection
        self.name = name

        self.events: Dict[str, Callable] = {}
        self.logger = logging.getLogger('events')

        # TODO: Refactor to pub/sub method

    def register(self, event_name: str):
        """Register an event"""
        def wrapper(callback: Callable):
            self.events[event_name] = callback
            return callback
        self.logger.debug(
            f'Registered new event: "{event_name}"'
        )
        return wrapper

    def submit(self, event: str, *args, **kwargs):
        """Push an event to the queue"""
        self.redis.lpush(self.name, str((event, args, kwargs)))

    def listen(self, start: int = 0, end: int = -1, buffer_time: int = 1) -> Generator:
        """Listen for events from the queue"""
        while True:
            events = self.redis.lrange(self.name, start, end)

            for event in events:
                try:
                    name, args, kwargs = eval(event)
                    self.logger.debug(
                        f'Got event for "{name}" with {args} and {kwargs}'
                    )
                    yield self.events[name], args, kwargs
                except KeyError:
                    self.logger.warning(
                        f'No callback found for "{name}"'
                    )
                except Exception as e:
                    self.logger.warning(
                        f'Failed to evaluate task: {e}'
                    )
                finally:
                    self.logger.debug(
                        f'Removing "{name}" from queue'
                    )
                    self.redis.lpop(self.name, 1)

            time.sleep(buffer_time)
