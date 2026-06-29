"""
Asset loader for fonts, avatars, and wallpaper images.

Handles graceful fallback when external assets are not found:
- Fonts: falls back to Pillow default
- Avatars: generates initial-based circular avatars via Pillow
- Wallpaper: generates a subtle pattern programmatically
"""

import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from config import (
    AVATAR_SIZE,
    CANVAS_SIZE,
    FONTS_DIR,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_XL,
    FONT_SIZE_XS,
    FONT_SIZE_HEADER,
    FONT_SIZE_STATUS,
    WALLPAPERS_DIR,
)

logger = logging.getLogger(__name__)


class AssetLoader:
    """Lazy-loads and caches fonts, avatars, and wallpapers."""

    _instance: Optional["AssetLoader"] = None
    _fonts: Dict[int, ImageFont.FreeTypeFont] = {}
    _avatars: Dict[str, Image.Image] = {}
    _wallpaper: Optional[Image.Image] = None

    def __new__(cls):
        """Singleton pattern — one loader for the whole app."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._font_path = self._find_font()
        self._fonts = {}
        self._avatars = {}
        self._wallpaper = None
        logger.info(f"AssetLoader initialized. Font path: {self._font_path}")

    # ------------------------------------------------------------------
    # Font loading
    # ------------------------------------------------------------------

    def _find_font(self) -> Optional[Path]:
        """
        Search for a usable TrueType font.

        Priority:
        1. assets/fonts/NotoSans-Regular.ttf
        2. assets/fonts/*.ttf (first found)
        3. Common system font paths
        4. None (will use Pillow default)
        """
        # Check project fonts dir
        if FONTS_DIR.exists():
            noto = FONTS_DIR / "NotoSans-Regular.ttf"
            if noto.exists():
                return noto
            # Any TTF in the fonts dir
            for ttf in FONTS_DIR.glob("*.ttf"):
                return ttf

        # Common system fonts (Windows Emoji/Sans → Linux → Mac)
        system_fonts = [
            Path("C:/Windows/Fonts/seguiemj.ttf"),
            Path("C:/Windows/Fonts/arial.ttf"),
            Path("C:/Windows/Fonts/segoeui.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"),
            Path("/System/Library/Fonts/Helvetica.ttc"),
            Path("/System/Library/Fonts/SFCompact.ttf"),
        ]
        for sp in system_fonts:
            if sp.exists():
                return sp

        logger.warning("No TrueType font found. Using Pillow default bitmap font.")
        return None

    def get_font(self, size: int) -> ImageFont.FreeTypeFont:
        """
        Get a font at the specified pixel size (cached).

        Args:
            size: Font size in pixels.

        Returns:
            PIL ImageFont.
        """
        if size not in self._fonts:
            if self._font_path:
                try:
                    self._fonts[size] = ImageFont.truetype(str(self._font_path), size)
                except Exception as e:
                    logger.warning(f"Failed to load font at size {size}: {e}")
                    self._fonts[size] = ImageFont.load_default()
            else:
                self._fonts[size] = ImageFont.load_default()
        return self._fonts[size]

    @property
    def font_xs(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_XS)

    @property
    def font_sm(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_SM)

    @property
    def font_md(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_MD)

    @property
    def font_lg(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_LG)

    @property
    def font_xl(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_XL)

    @property
    def font_header(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_HEADER)

    @property
    def font_status(self) -> ImageFont.FreeTypeFont:
        return self.get_font(FONT_SIZE_STATUS)

    # ------------------------------------------------------------------
    # Avatar generation
    # ------------------------------------------------------------------

    def get_avatar(
        self,
        name: str,
        color: Tuple[int, int, int],
        size: int = AVATAR_SIZE,
    ) -> Image.Image:
        """
        Generate or retrieve a circular initials-based avatar.

        Args:
            name: Display name (first letter is used).
            color: Background RGB color.
            size: Avatar diameter in pixels.

        Returns:
            PIL RGBA Image with circular avatar.
        """
        cache_key = f"{name}_{color}_{size}"
        if cache_key in self._avatars:
            return self._avatars[cache_key]

        # Create circular avatar
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw filled circle
        draw.ellipse([0, 0, size - 1, size - 1], fill=color)

        # Draw initial letter
        initial = name[0].upper() if name else "?"
        font = self.get_font(size // 2)

        # Get text bounding box for centering
        bbox = draw.textbbox((0, 0), initial, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (size - text_w) // 2
        text_y = (size - text_h) // 2 - bbox[1]  # adjust for baseline offset

        draw.text((text_x, text_y), initial, fill=(255, 255, 255), font=font)

        self._avatars[cache_key] = img
        return img

    # ------------------------------------------------------------------
    # Wallpaper generation
    # ------------------------------------------------------------------

    def get_wallpaper(
        self,
        theme_colors: dict,
        size: Tuple[int, int] = CANVAS_SIZE,
    ) -> Image.Image:
        """
        Load wallpaper from assets or generate a subtle WhatsApp-style pattern.

        Args:
            theme_colors: Theme color dict (needs 'chat_bg' and 'wallpaper_tint').
            size: Canvas size tuple.

        Returns:
            PIL RGB Image sized to canvas.
        """
        cache_key = f"wp_{theme_colors['name']}_{size}"
        if cache_key in self._avatars:  # reuse avatar cache dict
            return self._avatars[cache_key]

        # Try loading from assets
        if WALLPAPERS_DIR.exists():
            for ext in ("png", "jpg", "jpeg"):
                pattern = f"wa_bg_{theme_colors['name']}.{ext}"
                wp_path = WALLPAPERS_DIR / pattern
                if wp_path.exists():
                    try:
                        img = Image.open(wp_path).convert("RGB").resize(size)
                        self._avatars[cache_key] = img
                        return img
                    except Exception as e:
                        logger.warning(f"Failed to load wallpaper {wp_path}: {e}")

        # Generate programmatic wallpaper with subtle doodle pattern
        img = self._generate_wallpaper_pattern(theme_colors, size)
        self._avatars[cache_key] = img
        return img

    def _generate_wallpaper_pattern(
        self,
        theme_colors: dict,
        size: Tuple[int, int],
    ) -> Image.Image:
        """
        Generate a subtle WhatsApp-like wallpaper pattern.

        Creates a dark/light background with faint doodle-like shapes
        (small icons: circles, hearts, stars, chat bubbles) scattered randomly.
        """
        import random as rng

        bg_color = theme_colors["chat_bg"]
        tint = theme_colors["wallpaper_tint"]

        img = Image.new("RGB", size, bg_color)
        draw = ImageDraw.Draw(img)

        # Seed for consistent pattern
        rng.seed(42)

        # Draw subtle doodle shapes
        icon_color = tuple(
            min(255, c + 8) for c in tint
        )  # very slightly lighter than tint

        for _ in range(120):
            x = rng.randint(0, size[0])
            y = rng.randint(0, size[1])
            shape_type = rng.choice(["circle", "square", "diamond", "dot"])
            s = rng.randint(6, 14)

            if shape_type == "circle":
                draw.ellipse([x, y, x + s, y + s], outline=icon_color)
            elif shape_type == "square":
                draw.rectangle([x, y, x + s, y + s], outline=icon_color)
            elif shape_type == "diamond":
                half = s // 2
                draw.polygon(
                    [(x + half, y), (x + s, y + half), (x + half, y + s), (x, y + half)],
                    outline=icon_color,
                )
            elif shape_type == "dot":
                draw.ellipse([x, y, x + 4, y + 4], fill=icon_color)

        return img
