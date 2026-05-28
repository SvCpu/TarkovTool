import threading
from typing import Callable, Type

from .events import *
import logging

class EventManger:
    _instance = None
    _events:dict[str, list] = {}
    _enable = False
    _logparser = None
    @classmethod
    def register(cls, event: Type[Event], handler: Callable) -> None:
        if event in ALL_EVENTS:
            event_name = event._event_name
            cls._events.setdefault(event_name, []).append(handler)
    @classmethod
    def _trigger(cls, event: Event):
        if cls._enable:
            for handler in cls._events.get(event.event_name(), []):
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
    @classmethod
    def Disable(cls):
        cls._trigger(event=ON_SHUTDOWN())
        cls._enable = False
    def __bool__(cls):
        return cls._enable