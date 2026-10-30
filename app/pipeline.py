"""Speech-to-text, translation and text-to-speech building blocks."""
import asyncio
import io
import logging
import wave
from functools import lru_cache
from pathlib import Path

import httpx
import numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import VadOptions, get_speech_timestamps
from piper import PiperVoice
from piper.download_voices import download_voice

import config

log = logging.getLogger("pipeline")
SR = 16000


class Segmenter:
    """Buffers 16 kHz audio and cuts out one utterance whenever the speaker pauses."""

    def __init__(self):
        self.buf = np.zeros(0, dtype=np.float32)
        self.unchecked = 0
        self.vad = VadOptions(min_silence_duration_ms=config.SILENCE_MS, speech_pad_ms=200)

    def feed(self, pcm16: bytes) -> np.ndarray | None:
        chunk = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32) / 32768
        self.buf = np.concatenate([self.buf, chunk])
        self.unchecked += len(chunk)
        if self.unchecked < SR // 4:  # run VAD at most every 250 ms
            return None
        self.unchecked = 0

        speech = get_speech_timestamps(self.buf, self.vad)
        if not speech:
            self.buf = self.buf[-SR // 2:]  # keep a little audio so word onsets aren't clipped
            return None
        start, end = speech[0]["start"], speech[-1]["end"]
        paused = len(self.buf) - end >= config.SILENCE_MS * SR // 1000
        too_long = end - start >= config.MAX_UTTERANCE_S * SR
        if not (paused or too_long):
            return None
        utterance, self.buf = self.buf[start:end], self.buf[end:]
        return utterance


class STT:
    def __init__(self):
        log.info("loading whisper %s on %s", config.WHISPER_MODEL, config.WHISPER_DEVICE)
        self.model = WhisperModel(
            config.WHISPER_MODEL, device=config.WHISPER_DEVICE, compute_type=config.WHISPER_COMPUTE
        )
        self.lock = asyncio.Lock()

    def _run(self, audio: np.ndarray, lang: str | None) -> tuple[str, str]:
        segments, info = self.model.transcribe(
            audio, language=lang, beam_size=1, condition_on_previous_text=False
        )
        # drop Whisper's typical hallucinations on noise ("Thank you.", etc.)
        text = " ".join(
            s.text.strip() for s in segments if not (s.no_speech_prob > 0.6 and s.avg_logprob < -1)
        )
        return text.strip(), info.language

    async def transcribe(self, audio: np.ndarray, lang: str | None) -> tuple[str, str]:
        async with self.lock:
            return await asyncio.to_thread(self._run, audio, lang)


class Translator:
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=config.MT_URL, timeout=30)
        self.cache: dict[tuple[str, str, str], str] = {}

    async def languages(self) -> list[str]:
        try:
            r = await self.client.get("/languages")
            return [lang["code"] for lang in r.json()]
        except httpx.HTTPError:
            return []

    async def translate(self, text: str, src: str, tgt: str) -> str | None:
        key = (text, src, tgt)
        if key not in self.cache:
            try:
                r = await self.client.post(
                    "/translate", json={"q": text, "source": src, "target": tgt, "format": "text"}
                )
                r.raise_for_status()
            except httpx.HTTPError as e:
                log.warning("translate %s->%s failed: %s", src, tgt, e)
                return None
            if len(self.cache) > 5000:
                self.cache.clear()
            self.cache[key] = r.json()["translatedText"]
        return self.cache[key]


class TTS:
    def __init__(self):
        self.dir = Path(config.VOICE_DIR)
        self.dir.mkdir(parents=True, exist_ok=True)
        for voice in config.VOICES.values():
            download_voice(voice, self.dir)  # no-op when already downloaded

    @lru_cache(maxsize=None)
    def _voice(self, lang: str) -> PiperVoice:
        return PiperVoice.load(self.dir / f"{config.VOICES[lang]}.onnx")

    def _run(self, text: str, lang: str) -> bytes:
        out = io.BytesIO()
        with wave.open(out, "wb") as wav:
            self._voice(lang).synthesize_wav(text, wav)
        return out.getvalue()

    async def speak(self, text: str, lang: str) -> bytes | None:
        if lang not in config.VOICES:
            return None  # captions only for this language
        return await asyncio.to_thread(self._run, text, lang)
