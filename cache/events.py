
from typing import Tuple, Dict, Generator, Callable
from threading import Thread
from redis import Redis

import logging

class EventQueue:
    def __init__(self, name: str, connection: Redis) -> None:
        self.name = name
        self.redis = connection
        self.events: Dict[str, Callable] = {}
        self.logger = logging.getLogger(self.name)
        self.channel = self.redis.pubsub()

    def register(self, event_name: str):
        """Register an event"""
        def wrapper(callback: Callable):
            self.events[event_name] = callback
            self.logger.debug(f'Registered new event: "{event_name}"')
            return callback
        return wrapper

    def submit(self, event: str, *args, **kwargs):
        """Push an event to the queue"""
        self.redis.publish(self.name, str((event, args, kwargs)))
        self.logger.debug(f'Submitted event "{event}" to pubsub channel')

    def poll(self, timeout: int = 0) -> Tuple[Callable, Tuple, Dict] | None:
        """Poll for events from the queue"""
        if self.name.encode() not in self.channel.channels:
            # Ensure we are subscribed to the channel
            self.channel.subscribe(self.name)
            self.logger.info(f'Subscribed to pubsub channel "{self.name}".')

        message = self.channel.get_message(
            ignore_subscribe_messages=True,
            timeout=timeout
        )

        if message is None:
            return

        try:
            name, args, kwargs = eval(message['data'])
            self.logger.debug(f'Got event for "{name}" with {args} and {kwargs}')
            return self.events[name], args, kwargs
        except KeyError:
            self.logger.warning(f'No callback found for "{name}"')
        except Exception as e:
            self.logger.warning(f'Failed to evaluate task: {e}')

    def listen(self) -> Generator:
        """Listen for events from the queue"""
        self.channel.subscribe(self.name)
        self.logger.info('Listening to pubsub channel...')

        for message in self.channel.listen():
            try:
                if message['data'] == 1: continue
                name, args, kwargs = eval(message['data'])
                self.logger.debug(f'Got event for "{name}" with {args} and {kwargs}')
                yield self.events[name], args, kwargs
            except KeyError:
                self.logger.warning(f'No callback found for "{name}"')
            except Exception as e:
                self.logger.warning(f'Failed to evaluate task: {e}')

    def run(self, on_failure: Callable | None = None) -> None:
        """Run the event loop"""
        default_handler = lambda e: self.logger.error(
            f'An error occurred while processing event: {e}',
            exc_info=True
        )

        # Use default error handler, if on_failure is not provided
        on_failure = on_failure or default_handler

        for func, args, kwargs in self.listen():
            try:
                func(*args, **kwargs)
            except SystemExit:
                break
            except Exception as e:
                on_failure(e)

    def run_async(self, on_failure: Callable | None = None) -> Thread:
        """Listen & run events in a separate thread"""
        thread = Thread(target=self.run, args=(on_failure,), daemon=True)
        thread.start()
        return thread
