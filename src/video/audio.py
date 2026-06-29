"""
Audio mixer for WhatsApp Reel Generator.

Handles:
- Notification sound on first message
- Typing sounds between messages
- Optional gTTS text-to-speech narration

All audio is optional — gracefully skips if sound files are missing.
"""

import logging
from pathlib import Path
from typing import List, Optional

from config import SOUNDS_DIR

logger = logging.getLogger(__name__)


class AudioMixer:
    """Mix audio effects into the reel video."""

    def __init__(self):
        """Initialize and check for available sound files."""
        self.notification_path = SOUNDS_DIR / "notification.mp3"
        self.typing_path = SOUNDS_DIR / "typing.mp3"

        self._has_notification = self.notification_path.exists()
        self._has_typing = self.typing_path.exists()

        if not self._has_notification:
            logger.info(
                f"Notification sound not found at {self.notification_path}. "
                "Audio will be skipped."
            )
        if not self._has_typing:
            logger.info(
                f"Typing sound not found at {self.typing_path}. "
                "Audio will be skipped."
            )

    @property
    def has_sounds(self) -> bool:
        """Check if any sound files are available."""
        return self._has_notification or self._has_typing

    def create_mixed_audio(
        self,
        message_times: List[float],
        total_duration: float,
        output_path: str,
    ) -> Optional[str]:
        """
        Create a mixed audio track with notification and typing sounds.

        Args:
            message_times: List of timestamps (seconds) when each message appears.
            total_duration: Total video duration in seconds.
            output_path: Where to save the mixed audio MP3.

        Returns:
            Path to the mixed audio file, or None if no sounds available.
        """
        if not self.has_sounds:
            return None

        try:
            from moviepy import (
                AudioFileClip,
                CompositeAudioClip,
            )
            from moviepy.audio.AudioClip import AudioClip
            import numpy as np

            clips = []

            # Add notification sound at first message
            if self._has_notification and len(message_times) > 0:
                try:
                    notif = AudioFileClip(str(self.notification_path))
                    # Trim to max 1 second
                    if notif.duration > 1.0:
                        notif = notif.subclipped(0, 1.0)
                    # Set start time to first message
                    notif = notif.with_start(message_times[0])
                    # Lower volume
                    notif = notif.with_volume_scaled(0.5)
                    clips.append(notif)
                except Exception as e:
                    logger.warning(f"Failed to load notification sound: {e}")

            # Add typing sounds between speaker changes
            if self._has_typing and len(message_times) > 1:
                try:
                    typing_clip = AudioFileClip(str(self.typing_path))
                    if typing_clip.duration > 0.8:
                        typing_clip = typing_clip.subclipped(0, 0.8)
                    typing_clip = typing_clip.with_volume_scaled(0.3)

                    # Add at every 3rd message transition
                    for i in range(2, len(message_times), 3):
                        tc = typing_clip.copy()
                        start = max(0, message_times[i] - 0.5)
                        tc = tc.with_start(start)
                        clips.append(tc)
                except Exception as e:
                    logger.warning(f"Failed to load typing sound: {e}")

            if not clips:
                return None

            # Create silence base track
            silence = AudioClip(
                lambda t: np.zeros((1, 2)),
                duration=total_duration,
                fps=44100,
            )
            silence = silence.with_fps(44100)

            clips.insert(0, silence)
            mixed = CompositeAudioClip(clips)

            # Export
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            mixed.write_audiofile(str(out_path), fps=44100, logger=None)

            # Cleanup
            for c in clips:
                try:
                    c.close()
                except Exception:
                    pass

            logger.info(f"Mixed audio saved: {output_path}")
            return str(out_path)

        except ImportError:
            logger.warning("MoviePy audio tools not available. Skipping audio.")
            return None
        except Exception as e:
            logger.warning(f"Audio mixing failed: {e}. Continuing without audio.")
            return None

    def generate_tts_narration(
        self,
        text: str,
        output_path: str,
        lang: str = "hi",
    ) -> Optional[str]:
        """
        Generate text-to-speech narration using gTTS.

        Args:
            text: Text to narrate.
            output_path: Where to save the audio file.
            lang: Language code (default: Hindi).

        Returns:
            Path to the generated audio file, or None on failure.
        """
        try:
            from gtts import gTTS

            tts = gTTS(text=text, lang=lang, slow=False)
            out_path = Path(output_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            tts.save(str(out_path))
            logger.info(f"TTS narration saved: {output_path}")
            return str(out_path)

        except ImportError:
            logger.warning("gTTS not installed. Skipping TTS narration.")
            return None
        except Exception as e:
            logger.warning(f"TTS generation failed: {e}")
            return None
