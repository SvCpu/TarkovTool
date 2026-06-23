from .events import *

from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Type
import inspect
import logging
import traceback

logger = logging.getLogger(__name__)

class EventManger:
    _instance = None
    _events:dict[str, list] = {}
    _enable = False
    _logparser = None
    _executor = ThreadPoolExecutor(max_workers=8)
    @classmethod
    def register(cls, event: Type[Event], handler: Callable[[Event],None]) -> None:
        if not inspect.isclass(event):
            raise TypeError("")
        if event in ALL_EVENTS:
            event_name = event.event_name
            cls._events.setdefault(event_name, []).append(handler)
            logger.info(f'register event:{event.event_name}')
    @classmethod
    def _trigger(cls, event: Event):
        if not isinstance(event, Event):
            logger.error(
                f"Expected a class, but got an instance of {type(cls).__name__}. "
                f"Pass the class itself instead."
            )
            return
        logger.info(f'trigger event:{event.event_name}')
        if cls._enable:
            for handler in cls._events.get(event.event_name, []):
                def safe_call():
                    try:
                        handler(event)
                    except Exception:
                        logger.debug(f"Handler error: {traceback.format_exc(chain=True)}")
                        logger.error(f"Handler error: {traceback.format_exc()}")
                cls._executor.submit(safe_call)
    @classmethod
    def Enable(cls):
        cls._enable = True
        cls._trigger(event=ON_STARTUP())
        logger.info('EventManger Enable')
    @classmethod
    def Disable(cls):
        cls._trigger(event=ON_SHUTDOWN())
        cls._enable = False
        logger.info('EventManger Disable')
    @classmethod
    def active(cls)->bool:
        return cls._enable