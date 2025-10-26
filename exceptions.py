
from concurrent.futures import ThreadPoolExecutor
from app.common import officer
from types import TracebackType
import sys

executor = ThreadPoolExecutor(max_workers=4)
ignored_types = (KeyboardInterrupt, SystemExit)

def global_exception_handler(exc_type: type, exc_value: Exception, exc_traceback: TracebackType) -> None:
    if isinstance(exc_value, ignored_types):
        return

    executor.submit(
        officer.call,
        'An unhandled exception occurred in the application.',
        exc_info=exc_value
    )

sys.excepthook = global_exception_handler
