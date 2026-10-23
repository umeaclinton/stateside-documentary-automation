import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
AUDIO_ASSETS_DIR = ASSETS_DIR / "audio"
FONT_ASSETS_DIR = ASSETS_DIR / "fonts"

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

# Content Niche & Configuration
CONTENT_NICHE = os.getenv("CONTENT_NICHE", "Psychology & Human Behavior")

# Microsoft Edge-TTS Voice Configuration
VOICE_NAME = os.getenv("VOICE_NAME", "en-US-ChristopherNeural")
VOICE_RATE = os.getenv("VOICE_RATE", "+0%")
VOICE_PITCH = os.getenv("VOICE_PITCH", "+0Hz")

# Video Composition Settings (9:16 Vertical Shorts)
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1080"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "1920"))
FPS = int(os.getenv("FPS", "30"))
MIN_CLIP_DURATION = float(os.getenv("MIN_CLIP_DURATION", "3.0"))
MAX_CLIP_DURATION = float(os.getenv("MAX_CLIP_DURATION", "5.0"))
MAX_VIDEO_DURATION_SECONDS = int(os.getenv("MAX_VIDEO_DURATION_SECONDS", "55"))

# Caption / Subtitle Style Settings
FONT_NAME = os.getenv("FONT_NAME", "Arial")
FONT_SIZE = int(os.getenv("FONT_SIZE", "68"))
FONT_COLOR = os.getenv("FONT_COLOR", "&H00FFFFFF")         # BGR/Hex White
OUTLINE_COLOR = os.getenv("OUTLINE_COLOR", "&H00000000")   # Black border
HIGHLIGHT_COLOR = os.getenv("HIGHLIGHT_COLOR", "&H0000FFFF") # Gold/Yellow accent

# YouTube Data API Credentials
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", str(BASE_DIR / "client_secret.json"))
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", str(BASE_DIR / "oauth_token.json"))
YOUTUBE_PRIVACY_STATUS = os.getenv("YOUTUBE_PRIVACY_STATUS", "public") # "public", "unlisted", "private"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
