import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = Path(os.getenv("INPUT_DIR", BASE_DIR / "input"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", BASE_DIR / "output"))

# Whisper configuration
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "medium")

# Translation configuration
LIBRETRANSLATE_URL = os.getenv("LIBRETRANSLATE_URL", "http://localhost:5000/translate")
SOURCE_LANG = os.getenv("SOURCE_LANG", "en")
TARGET_LANG = os.getenv("TARGET_LANG", "es")

# Audio extraction settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Ensure directories exist
INPUT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
