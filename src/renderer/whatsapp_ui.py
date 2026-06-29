"""
Full WhatsApp screen renderer.

Composes the complete WhatsApp chat UI:
- Status bar (time, battery, signal)
- Header (back arrow, avatar, contact name, online status)
- Chat area with wallpaper background
- Message bubbles stacked vertically with auto-scroll
- Typing indicator
- Input bar at bottom
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw

from config import (
    AVATAR_SIZE,
    BUBBLE_SPACING,
    CANVAS_HEIGHT,
    CANVAS_SIZE,
    CANVAS_WIDTH,
    CHAT_AREA_TOP,
    CHAT_PADDING_X,
    CHAT_PADDING_Y,
    FONT_SIZE_LG,
    FONT_SIZE_MD,
    FONT_SIZE_SM,
    FONT_SIZE_STATUS,
    HEADER_HEIGHT,
    STATUS_BAR_HEIGHT,
    get_theme,
)
from src.renderer.assets import AssetLoader
from src.renderer.bubbles import draw_bubble, draw_typing_indicator

logger = logging.getLogger(__name__)


class WhatsAppRenderer:
    """Renders WhatsApp chat frames for video generation."""

    INPUT_BAR_HEIGHT = 130

    def __init__(self, theme: str = "dark"):
        """
        Initialize renderer with a theme.

        Args:
            theme: "dark" or "light".
        """
        self.theme_name = theme
        self.theme = get_theme(theme)
        self.assets = AssetLoader()
        self._wallpaper: Optional[Image.Image] = None

    def _get_wallpaper(self) -> Image.Image:
        """Get or generate the wallpaper background (cached)."""
        if self._wallpaper is None:
            self._wallpaper = self.assets.get_wallpaper(self.theme, CANVAS_SIZE)
        return self._wallpaper

    # ------------------------------------------------------------------
    # Status bar
    # ------------------------------------------------------------------
    def _draw_status_bar(self, draw: ImageDraw.Draw):
        """Draw the phone status bar at the very top."""
        bg = self.theme["status_bar_bg"]
        text_color = self.theme["header_text"] if self.theme_name == "light" else self.theme["text_primary"]
        font = self.assets.get_font(FONT_SIZE_STATUS)

        # Background
        draw.rectangle([0, 0, CANVAS_WIDTH, STATUS_BAR_HEIGHT], fill=bg)

        # Time (left)
        now_str = datetime.now().strftime("%I:%M")
        text_y = (STATUS_BAR_HEIGHT - FONT_SIZE_STATUS) // 2
        draw.text((36, text_y), now_str, fill=text_color, font=font)

        # Battery + signal icons (right) — simplified text representation
        right_text = "4G"
        bbox = draw.textbbox((0, 0), right_text, font=font)
        rw = bbox[2] - bbox[0]
        draw.text((CANVAS_WIDTH - rw - 36, text_y), right_text, fill=text_color, font=font)

        # Signal bars (center-right area) — draw small rectangles
        signal_x = CANVAS_WIDTH - 200
        signal_y = text_y + (FONT_SIZE_STATUS - 20) // 2
        bar_colors = text_color
        for i in range(4):
            bar_h = 8 + i * 4
            draw.rectangle(
                [signal_x + i * 12, signal_y + (20 - bar_h), signal_x + i * 12 + 7, signal_y + 20],
                fill=bar_colors,
            )

    # ------------------------------------------------------------------
    # Header
    # ------------------------------------------------------------------
    def _draw_header(
        self,
        image: Image.Image,
        draw: ImageDraw.Draw,
        contact_name: str,
        avatar_color: Tuple[int, int, int],
        status_text: str = "online",
    ):
        """Draw the WhatsApp chat header with avatar and contact name."""
        bg = self.theme["header_bg"]
        name_color = self.theme["header_text"]
        status_color = self.theme["online_color"]
        icon_color = self.theme["header_icon"]

        header_y = STATUS_BAR_HEIGHT
        font_name = self.assets.get_font(FONT_SIZE_LG)
        font_status = self.assets.get_font(FONT_SIZE_SM)

        # Background
        draw.rectangle(
            [0, header_y, CANVAS_WIDTH, header_y + HEADER_HEIGHT],
            fill=bg,
        )

        # Back arrow (←)
        arrow_x = 24
        draw.text((arrow_x, header_y + (HEADER_HEIGHT - FONT_SIZE_LG) // 2), "<", fill=icon_color, font=font_name)

        # Avatar circle
        avatar_x = 80
        avatar_y = header_y + (HEADER_HEIGHT - AVATAR_SIZE) // 2
        avatar_img = self.assets.get_avatar(contact_name, avatar_color, AVATAR_SIZE)
        image.paste(avatar_img, (avatar_x, avatar_y), avatar_img)

        # Contact name
        name_x = avatar_x + AVATAR_SIZE + 20
        name_y = header_y + (HEADER_HEIGHT - FONT_SIZE_LG - FONT_SIZE_SM - 8) // 2
        draw.text((name_x, name_y), contact_name, fill=name_color, font=font_name, embedded_color=True)

        # Status text ("online")
        draw.text(
            (name_x, name_y + FONT_SIZE_LG + 8),
            status_text,
            fill=status_color,
            font=font_status,
            embedded_color=True,
        )

        # Right side icons (video call, phone, menu dots)
        icons_font = self.assets.get_font(FONT_SIZE_LG)
        right_icons = "..."
        bbox = draw.textbbox((0, 0), right_icons, font=icons_font)
        rw = bbox[2] - bbox[0]
        draw.text(
            (CANVAS_WIDTH - rw - 36, header_y + (HEADER_HEIGHT - FONT_SIZE_LG) // 2),
            right_icons,
            fill=icon_color,
            font=icons_font,
        )

    # ------------------------------------------------------------------
    # Input bar
    # ------------------------------------------------------------------
    def _draw_input_bar(self, draw: ImageDraw.Draw):
        """Draw the bottom input bar (message input + send button)."""
        bar_y = CANVAS_HEIGHT - self.INPUT_BAR_HEIGHT
        bg = self.theme["input_bar_bg"]
        text_color = self.theme["text_secondary"]
        font = self.assets.get_font(FONT_SIZE_MD)

        # Background
        draw.rectangle(
            [0, bar_y, CANVAS_WIDTH, CANVAS_HEIGHT],
            fill=self.theme["background"],
        )

        # Input field (rounded rect)
        input_margin = 24
        input_h = 90
        input_y = bar_y + (self.INPUT_BAR_HEIGHT - input_h) // 2
        draw.rounded_rectangle(
            [input_margin, input_y, CANVAS_WIDTH - 120, input_y + input_h],
            radius=45,
            fill=bg,
        )

        # Placeholder text
        draw.text(
            (input_margin + 60, input_y + (input_h - FONT_SIZE_MD) // 2),
            "Message",
            fill=text_color,
            font=font,
        )

        # Mic / Send button (green circle on right)
        mic_size = 90
        mic_x = CANVAS_WIDTH - mic_size - 20
        mic_y = input_y
        draw.ellipse(
            [mic_x, mic_y, mic_x + mic_size, mic_y + mic_size],
            fill=(0, 168, 132),  # WhatsApp green
        )

    # ------------------------------------------------------------------
    # Frame rendering
    # ------------------------------------------------------------------
    def render_frame(
        self,
        conversation: Dict[str, Any],
        messages_visible_count: int,
        show_typing: bool = False,
    ) -> Image.Image:
        """
        Render a single WhatsApp chat frame.

        Args:
            conversation: Full conversation dict with speakers, messages, _personas.
            messages_visible_count: Number of messages to show (0 = empty chat).
            show_typing: Whether to show typing indicator after last message.

        Returns:
            PIL Image (1080x1920).
        """
        # Create canvas with wallpaper
        wallpaper = self._get_wallpaper()
        frame = wallpaper.copy()
        draw = ImageDraw.Draw(frame)

        # Get persona info
        personas = conversation.get("_personas", {})
        speakers = {sp["id"]: sp["name"] for sp in conversation["speakers"]}

        # Determine who is the "other" person (shown in header)
        # The receiver (left-side person) is shown in the header
        header_speaker_id = None
        header_name = "Contact"
        header_color = (100, 100, 100)

        for pid, pdata in personas.items():
            if pdata["side"] == "left":
                header_speaker_id = pid
                header_name = pdata["name"]
                header_color = tuple(pdata["avatar_color"])
                break

        # If no left-side persona found, use speaker 1
        if header_speaker_id is None and personas:
            first_key = list(personas.keys())[0]
            header_name = personas[first_key]["name"]
            header_color = tuple(personas[first_key]["avatar_color"])

        # Draw status bar
        self._draw_status_bar(draw)

        # Draw header
        self._draw_header(frame, draw, header_name, header_color)

        # Draw input bar
        self._draw_input_bar(draw)

        # Draw messages
        if messages_visible_count > 0:
            messages = conversation["messages"][:messages_visible_count]
            self._draw_messages(frame, draw, messages, personas, speakers, show_typing)

        return frame

    def _draw_messages(
        self,
        image: Image.Image,
        draw: ImageDraw.Draw,
        messages: List[Dict],
        personas: Dict,
        speakers: Dict[str, str],
        show_typing: bool,
    ):
        """
        Draw message bubbles with auto-scroll when they overflow.

        Args:
            image: PIL Image to draw on.
            draw: ImageDraw for the image.
            messages: List of message dicts to render.
            personas: Persona metadata dict.
            speakers: Speaker ID → name mapping.
            show_typing: Show typing indicator after last message.
        """
        chat_top = CHAT_AREA_TOP + CHAT_PADDING_Y
        chat_bottom = CANVAS_HEIGHT - self.INPUT_BAR_HEIGHT - CHAT_PADDING_Y
        available_height = chat_bottom - chat_top

        # First pass: calculate all bubble heights to determine scroll offset
        bubble_infos = []
        temp_img = Image.new("RGB", CANVAS_SIZE, (0, 0, 0))

        cursor_y = 0
        prev_speaker = None

        for msg in messages:
            is_sender = self._is_sender(msg["speaker_id"], personas)

            # Add extra spacing between different speakers
            if prev_speaker is not None and prev_speaker != msg["speaker_id"]:
                cursor_y += BUBBLE_SPACING * 2
            else:
                cursor_y += BUBBLE_SPACING

            # Show tail only on first message or when speaker changes
            show_tail = prev_speaker != msg["speaker_id"]

            _, bh = draw_bubble(
                temp_img,
                msg["text"],
                0,
                cursor_y,
                is_sender=is_sender,
                theme=self.theme,
                timestamp=msg.get("timestamp", ""),
                is_read=msg.get("read", True),
                show_tail=show_tail,
            )

            bubble_infos.append({
                "msg": msg,
                "y_offset": cursor_y,
                "height": bh,
                "is_sender": is_sender,
                "show_tail": show_tail,
            })

            cursor_y += bh
            prev_speaker = msg["speaker_id"]

        # Add typing indicator height if needed
        typing_height = 50 if show_typing else 0
        total_content_height = cursor_y + typing_height

        # Calculate scroll offset
        scroll_offset = 0
        if total_content_height > available_height:
            scroll_offset = total_content_height - available_height + 20  # 20px bottom padding

        # Second pass: actually draw visible bubbles
        for info in bubble_infos:
            actual_y = chat_top + info["y_offset"] - scroll_offset

            # Skip if fully above visible area
            if actual_y + info["height"] < chat_top:
                continue
            # Skip if fully below visible area
            if actual_y > chat_bottom:
                continue

            draw_bubble(
                image,
                info["msg"]["text"],
                0,
                actual_y,
                is_sender=info["is_sender"],
                theme=self.theme,
                timestamp=info["msg"].get("timestamp", ""),
                is_read=info["msg"].get("read", True),
                show_tail=info["show_tail"],
            )

        # Draw typing indicator
        if show_typing:
            typing_y = chat_top + cursor_y + BUBBLE_SPACING - scroll_offset
            if chat_top <= typing_y <= chat_bottom - 40:
                # Determine who is typing (the next speaker)
                last_speaker = messages[-1]["speaker_id"] if messages else "s1"
                # The OTHER person is typing
                typing_is_sender = not self._is_sender(last_speaker, personas)
                draw_typing_indicator(
                    image, 0, typing_y, self.theme, is_sender=typing_is_sender
                )

    def _is_sender(self, speaker_id: str, personas: Dict) -> bool:
        """Determine if a speaker is the sender (right side)."""
        if speaker_id in personas:
            return personas[speaker_id]["side"] == "right"
        # Default: s1 = left (receiver shown in header), s2 = right (sender)
        return speaker_id == "s2"

    # ------------------------------------------------------------------
    # Full frame sequence generation
    # ------------------------------------------------------------------
    def render_all_frames(
        self,
        conversation: Dict[str, Any],
    ) -> List[Image.Image]:
        """
        Render the full sequence of frames for video animation.

        Frame sequence:
        - Frame 0: Empty chat (just header + wallpaper)
        - Frame 1: Message 1 + typing indicator
        - Frame 2: Message 2 + typing indicator
        - ...
        - Frame N-1: Message N-1 + typing indicator
        - Frame N: All messages, no typing indicator

        Args:
            conversation: Full conversation dict.

        Returns:
            List of PIL Images (one per frame).
        """
        messages = conversation["messages"]
        total_messages = len(messages)
        frames = []

        logger.info(f"Rendering {total_messages + 1} frames...")

        # Frame 0: Empty chat
        frame0 = self.render_frame(conversation, 0, show_typing=False)
        frames.append(frame0)

        # Frames 1 to N-1: progressive message reveal with typing indicator
        for i in range(1, total_messages):
            frame = self.render_frame(conversation, i, show_typing=True)
            frames.append(frame)

        # Frame N: All messages, no typing indicator
        frame_final = self.render_frame(conversation, total_messages, show_typing=False)
        frames.append(frame_final)

        logger.info(f"Rendered {len(frames)} frames successfully.")
        return frames
