import os

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")      # tiny/base/small/medium/large-v3-turbo
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")      # cpu or cuda
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8")   # int8 on CPU, float16 on GPU
MT_URL = os.getenv("MT_URL", "http://localhost:5000")    # LibreTranslate
VOICE_DIR = os.getenv("VOICE_DIR", "./voices")

# lang code -> Piper voice; a language without a voice gets captions only
VOICES = dict(
    pair.split("=")
    for pair in os.getenv(
        "VOICES",
        "en=en_US-lessac-medium,es=es_ES-davefx-medium,fr=fr_FR-siwis-medium,"
        "de=de_DE-thorsten-medium,hi=hi_IN-pratham-medium",
    ).split(",")
    if pair
)

SILENCE_MS = int(os.getenv("SILENCE_MS", "600"))         # pause that ends an utterance
MAX_UTTERANCE_S = float(os.getenv("MAX_UTTERANCE_S", "12"))
