import json
import logging
import threading
from websocket import WebSocketApp

logger = logging.getLogger(__name__)
WS_URL = "wss://socket.tarkov.dev"

# map
# streets-of-tarkov
# ground-zero
# customs
# factory
# interchange
# the-lab
# the-labyrinth
# lighthouse
# reserve
# shoreline
# terminal
# woods

class TarkovMonitorWS:
    def __init__(self, remote_id: str):
        self.remote_id = remote_id
        self._connected = threading.Event()
        self._ws = WebSocketApp(
            f"{WS_URL}/?sessionid={remote_id}-tm",
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open,
        )
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)

    def _on_open(self, ws):
        logger.info("Connected to socket.tarkov.dev")
        self._connected.set()

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            if data.get("type") == "ping":
                ws.send(json.dumps({"type": "pong"}))
        except json.JSONDecodeError:
            pass

    def _on_error(self, ws, error):
        logger.error("WebSocket error: %s", error)

    def _on_close(self, ws, close_status_code, close_msg):
        logger.info("Connection closed")

    def connect(self, timeout: float = 5):
        self._thread.start()
        if not self._connected.wait(timeout):
            raise TimeoutError("WebSocket connection timed out")

    def close(self):
        self._ws.close()

    def send_player_position(self, x: float, z: float, y: float, map_name: str, rotation: float = 0):
        payload = {
            "type": "command",
            "data": {
                "type": "playerPosition",
                "map": map_name,
                "position": {"x": x, "y": y, "z": z},
                "rotation": rotation,
            },
            "sessionID": self.remote_id,
        }
        self._ws.send(json.dumps(payload))

    def send_map(self, map_name: str):
        payload = {
            "type": "command",
            "data": {
                "type": "map",
                "value": map_name,
            },
            "sessionID": self.remote_id,
        }
        self._ws.send(json.dumps(payload))

    def send_command(self, command_type: str, **kwargs):
        payload = {
            "type": "command",
            "data": {
                "type": command_type,
                **kwargs,
            },
            "sessionID": self.remote_id,
        }
        self._ws.send(json.dumps(payload))