import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())
logging.getLogger("websocket").propagate = False