
from __future__ import annotations
from typing import Tuple, Dict, Generator, Callable
from threading import Thread
from redis import Redis

import logging

class EventQueue:
    def __init__(self, name: str, connection: Redis) -> None:
        self.redis = connection
        self.name = name

        self.events: Dict[str, Callable] = {}
        self.logger = logging.getLogger(self.name)
        self.channel = self.redis.pubsub()

    def register(self, event_name: str):
        """Register an event"""
        def wrapper(callback: Callable):
            self.events[event_name] = callback
            self.logger.debug(
                f'Registered new event: "{event_name}"'
            )
            return callback
        return wrapper

    def submit(self, event: str, *args, **kwargs):
        """Push an event to the queue"""
        self.redis.publish(self.name, str((event, args, kwargs)))
        self.logger.debug(f'Submitted event "{event}" to pubsub channel')

    def poll(self) -> Tuple[Callable, Tuple, Dict] | None:
        """Poll for events from the queue"""
        if self.name not in self.channel.channels:
            # Ensure we are subscribed to the channel
            self.channel.subscribe(self.name)

        message = self.channel.get_message()

        if not message:
            return

        if message.get('data') == 1:
            return

        try:
            name, args, kwargs = eval(message['data'])
            self.logger.debug(f'Got event for "{name}" with {args} and {kwargs}')
            return self.events[name], args
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
                self.logger.debug(
                    f'Got event for "{name}" with {args} and {kwargs}'
                )
                yield self.events[name], args, kwargs
            except KeyError:
                self.logger.warning(f'No callback found for "{name}"')
            except Exception as e:
                self.logger.warning(f'Failed to evaluate task: {e}')

    def listen_async(self) -> Thread:
        """Listen for events in a separate thread"""
        thread = Thread(target=self.listen, daemon=True)
        thread.start()
        return thread
