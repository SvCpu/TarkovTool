from .events import *

import inspect
import threading
from typing import Callable, Type
import logging

logger = logging.getLogger(__name__)

class EventManger:
    _instance = None
    _events:dict[str, list] = {}
    _enable = False
    _logparser = None
    @classmethod
    def register(cls, event: Type[Event], handler: Callable) -> None:
        if not inspect.isclass(event):
            raise TypeError("")
        if event in ALL_EVENTS:
            event_name = event._event_name
            cls._events.setdefault(event_name, []).append(handler)
            logger.info(f'register event:{event._event_name}')
    @classmethod
    def _trigger(cls, event: Event):
        if not inspect.isclass(event):
            logger.error(
                f"Expected a class, but got an instance of {type(cls).__name__}. "
                f"Pass the class itself instead."
            )
        logger.info(f'trigger event:{event._event_name}')
        if cls._enable:
            for handler in cls._events.get(event._event_name, []):
                def safe_call():
                    try:
                        handler(event=event)
                    except Exception as e:
                        print(f"Handler error: {e}")
                threading.Thread(target=safe_call, daemon=True).start()
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
    def active(cls)->bool:
        return cls._enable