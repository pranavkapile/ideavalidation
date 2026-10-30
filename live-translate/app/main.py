"""Live speech translation server: speakers in, translated captions + speech out."""
import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

import config
from pipeline import STT, TTS, Segmenter, Translator
from rooms import Room, rooms

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
log = logging.getLogger("app")
stt: STT
mt: Translator
tts: TTS


@asynccontextmanager
async def lifespan(_):
    global stt, mt, tts
    stt, mt, tts = STT(), Translator(), TTS()
    yield


app = FastAPI(lifespan=lifespan)
STATIC = Path(__file__).parent / "static"


@app.get("/")
async def index():
    return FileResponse(STATIC / "index.html")


@app.get("/api/languages")
async def languages():
    return {"translate": await mt.languages(), "voices": sorted(config.VOICES)}


async def deliver(room: Room, text: str, src: str, lang: str):
    """Translate + speak one utterance for one target language, then send to its listeners."""
    translated = text if lang == src else await mt.translate(text, src, lang)
    if not translated:
        return
    await room.send(lang, json={"text": translated, "original": text, "src": src, "lang": lang})
    if lang != src:  # same-language listeners get captions only
        audio = await tts.speak(translated, lang)
        if audio:
            await room.send(lang, audio=audio)


@app.websocket("/ws/speak/{room_id}")
async def speak(ws: WebSocket, room_id: str, lang: str = "auto"):
    """Receives 16 kHz mono PCM16 frames from a speaker."""
    await ws.accept()
    room, seg = rooms[room_id], Segmenter()
    queue: asyncio.Queue = asyncio.Queue()

    async def worker():  # one utterance at a time keeps captions in order
        while (audio := await queue.get()) is not None:
            text, src = await stt.transcribe(audio, None if lang == "auto" else lang)
            if not text:
                continue
            log.info("[%s] %s: %s", room_id, src, text)
            try:
                await ws.send_json({"text": text, "src": src})
            except Exception:
                pass  # speaker already left; still deliver to listeners
            await asyncio.gather(*(deliver(room, text, src, t) for t in room.languages()))

    task = asyncio.create_task(worker())
    try:
        while True:
            utterance = seg.feed(await ws.receive_bytes())
            if utterance is not None:
                if queue.qsize() > 3:  # falling behind: drop oldest instead of lagging
                    queue.get_nowait()
                queue.put_nowait(utterance)
    except WebSocketDisconnect:
        pass
    finally:
        queue.put_nowait(None)  # let the worker finish what was already said
        await task


@app.websocket("/ws/listen/{room_id}")
async def listen(ws: WebSocket, room_id: str, lang: str = "en"):
    await ws.accept()
    room = rooms[room_id]
    room.listeners[lang].add(ws)
    try:
        while True:
            await ws.receive_text()  # only used to detect disconnects
    except WebSocketDisconnect:
        pass
    finally:
        room.listeners[lang].discard(ws)
