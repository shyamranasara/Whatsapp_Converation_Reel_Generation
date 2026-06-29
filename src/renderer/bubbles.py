"""
WhatsApp chat bubble renderer.

Draws pixel-accurate WhatsApp message bubbles with:
- Rounded rectangle shape with tail
- Text wrapping at 60% canvas width
- Timestamp (tiny, bottom-right)
- Blue double ticks (read receipts)
- Typing indicator animation dots
"""

import textwrap
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from config import (
    BUBBLE_CORNER_RADIUS,
    BUBBLE_MAX_WIDTH_RATIO,
    BUBBLE_PADDING_X,
    BUBBLE_PADDING_Y,
    CANVAS_WIDTH,
    FONT_SIZE_MD,
    FONT_SIZE_XS,
    MESSAGE_TIMESTAMP_GAP,
)
from src.renderer.assets import AssetLoader


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """
    Word-wrap text to fit within max_width pixels.

    Args:
        text: The message text.
        font: PIL font to measure with.
        max_width: Maximum line width in pixels.

    Returns:
        List of wrapped text lines.
    """
    # Create a temporary draw surface for measurement
    tmp_img = Image.new("RGB", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp_img)

    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        bbox = tmp_draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]

        if line_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def _draw_rounded_rect(
    draw: ImageDraw.Draw,
    xy: Tuple[int, int, int, int],
    radius: int,
    fill: Tuple[int, int, int],
):
    """Draw a rounded rectangle."""
    x1, y1, x2, y2 = xy
    # Use pillow's built-in rounded rectangle
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def draw_bubble(
    image: Image.Image,
    text: str,
    x: int,
    y: int,
    is_sender: bool,
    theme: dict,
    timestamp: str = "",
    is_read: bool = True,
    show_tail: bool = True,
) -> Tuple[int, int]:
    """
    Draw a WhatsApp-style message bubble on the image.

    Args:
        image: PIL Image to draw on.
        text: Message text.
        x: X position (left edge for receiver, right edge for sender).
        y: Y position (top of bubble).
        is_sender: True = right-aligned green bubble; False = left-aligned grey bubble.
        theme: Color theme dict.
        timestamp: Timestamp string (e.g., "6:30 PM").
        is_read: Whether to show blue ticks (only for sender).
        show_tail: Whether to draw the bubble tail.

    Returns:
        (bubble_width, bubble_height) for layout stacking.
    """
    assets = AssetLoader()
    draw = ImageDraw.Draw(image)
    font = assets.get_font(FONT_SIZE_MD)
    timestamp_font = assets.get_font(FONT_SIZE_XS)

    # Colors
    bubble_color = theme["sender_bubble"] if is_sender else theme["receiver_bubble"]
    text_color = theme["text_primary"]
    ts_color = theme["timestamp_color"]

    # Calculate max text width (60% of canvas minus padding)
    max_text_width = int(CANVAS_WIDTH * BUBBLE_MAX_WIDTH_RATIO) - (BUBBLE_PADDING_X * 2)

    # Wrap text
    lines = _wrap_text(text, font, max_text_width)

    # Measure text block
    line_heights = []
    max_line_width = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_heights.append(h)
        max_line_width = max(max_line_width, w)

    line_spacing = 4
    text_block_height = sum(line_heights) + line_spacing * (len(lines) - 1)

    # Measure timestamp + ticks space
    ts_text = timestamp
    ts_bbox = draw.textbbox((0, 0), ts_text, font=timestamp_font)
    ts_width = ts_bbox[2] - ts_bbox[0]
    ts_height = ts_bbox[3] - ts_bbox[1]
    if is_sender:
        ts_width += 30  # reserve space for custom drawn double ticks

    # Check if timestamp fits on the last line
    last_line = lines[-1] if lines else ""
    last_line_bbox = draw.textbbox((0, 0), last_line, font=font)
    last_line_width = last_line_bbox[2] - last_line_bbox[0]

    ts_on_same_line = (last_line_width + ts_width + 20) <= max_text_width
    extra_ts_height = 0 if ts_on_same_line else ts_height + MESSAGE_TIMESTAMP_GAP

    # Calculate bubble dimensions
    bubble_content_width = max(max_line_width, ts_width) + BUBBLE_PADDING_X * 2
    if ts_on_same_line:
        bubble_content_width = max(
            bubble_content_width,
            last_line_width + ts_width + 20 + BUBBLE_PADDING_X * 2,
        )
    bubble_content_width = min(bubble_content_width, int(CANVAS_WIDTH * BUBBLE_MAX_WIDTH_RATIO))
    bubble_height = text_block_height + extra_ts_height + BUBBLE_PADDING_Y * 2

    # Tail width
    tail_w = 14 if show_tail else 0

    total_bubble_width = bubble_content_width + tail_w

    # Position the bubble
    if is_sender:
        # Right-aligned
        bubble_x = CANVAS_WIDTH - 28 - total_bubble_width
        tail_x = bubble_x + bubble_content_width
    else:
        # Left-aligned
        bubble_x = 28 + tail_w
        tail_x = 28

    bubble_y = y

    # Draw bubble background
    _draw_rounded_rect(
        draw,
        (bubble_x, bubble_y, bubble_x + bubble_content_width, bubble_y + bubble_height),
        BUBBLE_CORNER_RADIUS,
        bubble_color,
    )

    # Draw tail triangle
    if show_tail:
        if is_sender:
            # Right tail
            tail_points = [
                (bubble_x + bubble_content_width, bubble_y + 6),
                (bubble_x + bubble_content_width + tail_w, bubble_y),
                (bubble_x + bubble_content_width, bubble_y + 24),
            ]
        else:
            # Left tail
            tail_points = [
                (bubble_x, bubble_y + 6),
                (bubble_x - tail_w, bubble_y),
                (bubble_x, bubble_y + 24),
            ]
        draw.polygon(tail_points, fill=bubble_color)

    # Draw text lines
    text_x = bubble_x + BUBBLE_PADDING_X
    text_y = bubble_y + BUBBLE_PADDING_Y
    for i, line in enumerate(lines):
        draw.text((text_x, text_y), line, fill=text_color, font=font, embedded_color=True)
        text_y += line_heights[i] + line_spacing

    # Draw timestamp (and ticks for sender)
    if ts_on_same_line:
        ts_x = bubble_x + bubble_content_width - BUBBLE_PADDING_X - ts_width
        ts_y = bubble_y + bubble_height - BUBBLE_PADDING_Y - ts_height
    else:
        ts_x = bubble_x + bubble_content_width - BUBBLE_PADDING_X - ts_width
        ts_y = text_y + MESSAGE_TIMESTAMP_GAP

    # Draw timestamp text
    draw.text((ts_x, ts_y), timestamp, fill=ts_color, font=timestamp_font)

    # Draw ticks for sender
    if is_sender:
        tick_x = ts_x + ts_width - 22
        tick_y = ts_y + (ts_height - 14) // 2
        tick_color = theme["tick_blue"] if is_read else theme["tick_grey"]
        
        # Left tick
        draw.line(
            [(tick_x, tick_y + 7), (tick_x + 5, tick_y + 12), (tick_x + 12, tick_y + 3)],
            fill=tick_color,
            width=3,
        )
        # Right tick
        draw.line(
            [(tick_x + 7, tick_y + 7), (tick_x + 12, tick_y + 12), (tick_x + 19, tick_y + 3)],
            fill=tick_color,
            width=3,
        )

    return total_bubble_width, bubble_height


def draw_typing_indicator(
    image: Image.Image,
    x: int,
    y: int,
    theme: dict,
    is_sender: bool = False,
) -> int:
    """
    Draw a WhatsApp "typing..." indicator bubble with three dots.

    Args:
        image: PIL Image to draw on.
        x: X position.
        y: Y position (top).
        theme: Color theme dict.
        is_sender: Which side to draw on.

    Returns:
        Height of the typing indicator bubble.
    """
    draw = ImageDraw.Draw(image)

    bubble_color = theme["receiver_bubble"] if not is_sender else theme["sender_bubble"]
    dot_color = theme["typing_dots"]

    bubble_w = 120
    bubble_h = 56

    if is_sender:
        bx = CANVAS_WIDTH - 28 - bubble_w
    else:
        bx = 36

    # Draw rounded bubble
    _draw_rounded_rect(
        draw,
        (bx, y, bx + bubble_w, y + bubble_h),
        BUBBLE_CORNER_RADIUS,
        bubble_color,
    )

    # Draw three dots
    dot_r = 7
    dot_spacing = 20
    start_x = bx + (bubble_w - 3 * dot_r * 2 - 2 * dot_spacing) // 2 + dot_r
    dot_y = y + bubble_h // 2

    for i in range(3):
        cx = start_x + i * (dot_r * 2 + dot_spacing)
        draw.ellipse(
            [cx - dot_r, dot_y - dot_r, cx + dot_r, dot_y + dot_r],
            fill=dot_color,
        )

    return bubble_h
