
from typing import Tuple, Dict, Generator, Callable, Any
from threading import Thread
from redis import Redis

import logging
import json

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
        payload = json.dumps({
            'event': event,
            'args': args,
            'kwargs': kwargs,
        })
        self.redis.publish(self.name, payload)
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
            return None

        try:
            decoded = self.decode_event(message['data'])

            if decoded is None:
                return None

            name, args, kwargs = decoded
            self.logger.debug(f'Got event for "{name}" with {args} and {kwargs}')
            return self.events[name], args, kwargs
        except KeyError:
            self.logger.warning(f'No callback found for "{name}"')
            return None
        except Exception as e:
            self.logger.warning(f'Failed to process task: {e}')

    def listen(self) -> Generator:
        """Listen for events from the queue"""
        self.channel.subscribe(self.name)
        self.logger.info('Listening to pubsub channel...')

        for message in self.channel.listen():
            try:
                if message['data'] == 1:
                    # Subscription confirmation message, ignoring that
                    continue

                decoded = self.decode_event(message['data'])
                if decoded is None:
                    continue

                name, args, kwargs = decoded
                self.logger.debug(f'Got event for "{name}" with {args} and {kwargs}')
                yield self.events[name], args, kwargs
            except KeyError:
                self.logger.warning(f'No callback found for "{name}"')
            except Exception as e:
                self.logger.warning(f'Failed to process task: {e}')

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

    def decode_event(self, data: Any) -> Tuple[str, Tuple, Dict] | None:
        """Decode an event payload from pubsub safely."""
        try:
            payload = json.loads(data)
        except (TypeError, json.JSONDecodeError) as e:
            # self.logger.warning(f'Failed to decode task payload: {e}')
            # return None

            # NOTE: Using unsafe decoder until all apps are migrated to the new event format
            return self.decode_event_unsafe(data)

        if not isinstance(payload, dict):
            self.logger.warning('Invalid task payload type')
            return None

        name = payload.get('event')
        args = payload.get('args', [])
        kwargs = payload.get('kwargs', {})

        if not isinstance(name, str):
            self.logger.warning('Invalid task payload: event name must be a string')
            return None

        if not isinstance(args, (list, tuple)):
            self.logger.warning('Invalid task payload: args must be a list or tuple')
            return None

        if not isinstance(kwargs, dict):
            self.logger.warning('Invalid task payload: kwargs must be a dict')
            return None

        return name, tuple(args), kwargs

    def decode_event_unsafe(self, data: Any) -> Tuple[str, Tuple, Dict]:
        """
        Decode an event payload from pubsub the old way.
        This will be removed after all applications have migrated to the new json format.
        """
        name, args, kwargs = eval(data)
        return name, tuple(args), kwargs
