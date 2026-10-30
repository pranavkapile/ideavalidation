"""In-memory rooms: who is listening in which language."""
from collections import defaultdict

from fastapi import WebSocket


class Room:
    def __init__(self):
        self.listeners: dict[str, set[WebSocket]] = defaultdict(set)

    def languages(self) -> set[str]:
        return {lang for lang, sockets in self.listeners.items() if sockets}

    async def send(self, lang: str, *, json: dict | None = None, audio: bytes | None = None):
        for ws in list(self.listeners[lang]):
            try:
                if json is not None:
                    await ws.send_json(json)
                if audio is not None:
                    await ws.send_bytes(audio)
            except Exception:
                self.listeners[lang].discard(ws)


rooms: dict[str, Room] = defaultdict(Room)
