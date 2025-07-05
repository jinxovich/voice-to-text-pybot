import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

DEFAULT_LANGUAGE = "auto"

SUPPORTED_LANGUAGES = {
    "auto": "Автоматически",
}

DEFAULT_SUMMARY_STYLE = "default"

SUMMARY_STYLES = {
    "default": {
        "name": "Стандартное",
        "prompt": "You are a helpful assistant. Summarize the user text concisely and informatively."
    },
    "short": {
        "name": "Очень коротко",
        "prompt": "You are a helpful assistant. Summarize the user text in one or two sentences."
    },
}

WHISPER_MODEL_SIZE = "small"
MAX_MESSAGE_LENGTH = 4096
TRANSCRIPTION_DISPLAY_CHUNK_SIZE = 3800
SUMMARY_DISPLAY_CHUNK_SIZE = 3800