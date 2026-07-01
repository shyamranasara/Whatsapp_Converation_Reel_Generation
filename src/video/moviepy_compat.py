"""
MoviePy version compatibility helper.
Supports both MoviePy v1.x (legacy) and MoviePy v2.x.
"""

import logging

logger = logging.getLogger(__name__)

# Detect MoviePy version and import correct components
try:
    # Try MoviePy v2 imports
    from moviepy import ImageClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
    try:
        from moviepy.audio.AudioClip import AudioClip
    except ImportError:
        from moviepy.editor import AudioClip
    MOVIEPY_V2 = True
    logger.info("MoviePy v2.x detected.")
except ImportError:
    # Fallback to MoviePy v1 imports
    try:
        from moviepy.editor import (
            ImageClip,
            concatenate_videoclips,
            AudioFileClip,
            CompositeAudioClip,
            AudioClip,
        )
        MOVIEPY_V2 = False
        logger.info("MoviePy v1.x detected.")
    except ImportError as e:
        logger.error(f"Failed to import MoviePy (v1 or v2): {e}")
        raise e


def subclip(clip, start, end):
    """Compatibility wrapper for trimming clips (subclip/subclipped)."""
    if MOVIEPY_V2:
        return clip.subclipped(start, end)
    else:
        return clip.subclip(start, end)


def with_start(clip, start_time):
    """Compatibility wrapper for setting clip start time (with_start/set_start)."""
    if MOVIEPY_V2:
        return clip.with_start(start_time)
    else:
        return clip.set_start(start_time)


def with_volume_scaled(clip, factor):
    """Compatibility wrapper for scaling clip volume (with_volume_scaled/volumex)."""
    if MOVIEPY_V2:
        return clip.with_volume_scaled(factor)
    else:
        return clip.volumex(factor)


def with_fps(clip, fps):
    """Compatibility wrapper for setting clip fps (with_fps/set_fps)."""
    if MOVIEPY_V2:
        return clip.with_fps(fps)
    else:
        return clip.set_fps(fps)


def with_audio(video_clip, audio_clip):
    """Compatibility wrapper for setting audio of a video clip (with_audio/set_audio)."""
    if MOVIEPY_V2:
        return video_clip.with_audio(audio_clip)
    else:
        return video_clip.set_audio(audio_clip)
