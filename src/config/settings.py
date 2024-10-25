import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# OpenAI settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DEFAULT_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 2048

# Audio settings
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1

# Image settings
DEFAULT_IMAGE_SIZE = "1024x1024"
DEFAULT_IMAGE_MODEL = "dall-e-2"
