"""
Configuration and settings for WhatsApp Reel Generator.
Loads environment variables and defines all global constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
SOUNDS_DIR = ASSETS_DIR / "sounds"
WALLPAPERS_DIR = ASSETS_DIR / "wallpapers"
OUTPUT_DIR = BASE_DIR / "output"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Canvas / Video
# ---------------------------------------------------------------------------
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920
CANVAS_SIZE = (CANVAS_WIDTH, CANVAS_HEIGHT)
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
MAX_VIDEO_SIZE_MB = 30

# ---------------------------------------------------------------------------
# Font sizes (pixels) — scaled for 1080x1920 reel readability
# ---------------------------------------------------------------------------
FONT_SIZE_XS = 28
FONT_SIZE_SM = 32
FONT_SIZE_MD = 44
FONT_SIZE_LG = 48
FONT_SIZE_XL = 54
FONT_SIZE_HEADER = 52
FONT_SIZE_STATUS = 30

# ---------------------------------------------------------------------------
# UI Dimensions — scaled for 1080x1920
# ---------------------------------------------------------------------------
STATUS_BAR_HEIGHT = 90
HEADER_HEIGHT = 160
CHAT_AREA_TOP = STATUS_BAR_HEIGHT + HEADER_HEIGHT
CHAT_PADDING_X = 36
CHAT_PADDING_Y = 28
BUBBLE_MAX_WIDTH_RATIO = 0.72  # 72% of canvas width for wider bubbles
BUBBLE_CORNER_RADIUS = 24
BUBBLE_PADDING_X = 32
BUBBLE_PADDING_Y = 20
BUBBLE_SPACING = 24
MESSAGE_TIMESTAMP_GAP = 12
AVATAR_SIZE = 100

# ---------------------------------------------------------------------------
# Color Palettes
# ---------------------------------------------------------------------------
DARK_THEME = {
    "name": "dark",
    "background": (11, 20, 26),           # #0B141A
    "header_bg": (32, 44, 51),             # #202C33
    "status_bar_bg": (32, 44, 51),         # #202C33
    "chat_bg": (11, 20, 26),               # #0B141A
    "sender_bubble": (0, 92, 75),          # #005C4B
    "receiver_bubble": (32, 44, 51),       # #202C33
    "text_primary": (233, 237, 239),       # #E9EDEF
    "text_secondary": (134, 150, 160),     # #8696A0
    "timestamp_color": (134, 150, 160),    # #8696A0
    "tick_blue": (83, 189, 235),           # #53BDEB
    "tick_grey": (134, 150, 160),          # #8696A0
    "online_color": (134, 150, 160),       # #8696A0
    "header_icon": (134, 150, 160),        # #8696A0
    "header_text": (233, 237, 239),        # #E9EDEF
    "divider": (38, 53, 61),               # #26353D
    "typing_dots": (134, 150, 160),        # #8696A0
    "wallpaper_tint": (8, 15, 20),         # slightly darker than bg
    "input_bar_bg": (32, 44, 51),          # #202C33
}

LIGHT_THEME = {
    "name": "light",
    "background": (229, 221, 213),         # #E5DDD5
    "header_bg": (0, 128, 105),            # #008069
    "status_bar_bg": (0, 110, 90),         # #006E5A
    "chat_bg": (229, 221, 213),            # #E5DDD5
    "sender_bubble": (220, 248, 198),      # #DCF8C6
    "receiver_bubble": (255, 255, 255),    # #FFFFFF
    "text_primary": (17, 27, 33),          # #111B21
    "text_secondary": (102, 119, 129),     # #667781
    "timestamp_color": (102, 119, 129),    # #667781
    "tick_blue": (83, 189, 235),           # #53BDEB
    "tick_grey": (102, 119, 129),          # #667781
    "online_color": (210, 237, 228),       # #D2EDE4
    "header_icon": (255, 255, 255),        # #FFFFFF
    "header_text": (255, 255, 255),        # #FFFFFF
    "divider": (200, 195, 190),            # #C8C3BE
    "typing_dots": (102, 119, 129),        # #667781
    "wallpaper_tint": (218, 210, 202),     # slightly darker
    "input_bar_bg": (240, 240, 240),       # #F0F0F0
}

def get_theme(name: str = "dark") -> dict:
    """Return the color palette dict for the requested theme."""
    if name == "light":
        return LIGHT_THEME
    return DARK_THEME

# ---------------------------------------------------------------------------
# Gemini defaults
# ---------------------------------------------------------------------------
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_TEMPERATURE = 0.9
DEFAULT_TOP_P = 0.95
AVG_SECONDS_PER_MESSAGE = 2.5
