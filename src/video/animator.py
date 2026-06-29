"""
Video animator — converts rendered PIL frames into MP4 video.

Uses MoviePy to create an H.264-encoded video at 30fps,
with correct per-frame durations from the conversation delays.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from moviepy import ImageClip, concatenate_videoclips, AudioFileClip
import numpy as np
from PIL import Image

from config import CANVAS_SIZE, OUTPUT_DIR, VIDEO_CODEC, AUDIO_CODEC, VIDEO_FPS

logger = logging.getLogger(__name__)


class VideoAnimator:
    """Converts a sequence of PIL frames into an MP4 video."""

    def create_video(
        self,
        frames: List[Image.Image],
        conversation: Dict,
        output_path: str,
        audio_path: Optional[str] = None,
        target_duration: Optional[float] = None,
    ) -> str:
        """
        Create an MP4 video from PIL image frames.

        Args:
            frames: List of PIL Images (each 1080x1920).
            conversation: Conversation dict (used for delay_ms values).
            output_path: Output file path for the MP4.
            audio_path: Optional audio file to overlay.
            target_duration: Target total duration in seconds (adjusts frame durations).

        Returns:
            The output file path.
        """
        

        # Calculate per-frame durations
        durations = self._calculate_frame_durations(
            conversation.get("messages", []),
            len(frames),
            target_duration,
        )

        logger.info(
            f"Creating video: {len(frames)} frames, "
            f"total duration: {sum(durations):.1f}s"
        )

        # Convert PIL images to numpy arrays and create clips
        clips = []
        for i, (frame, dur) in enumerate(zip(frames, durations)):
            # Ensure frame is RGB
            if frame.mode != "RGB":
                frame = frame.convert("RGB")
            arr = np.array(frame)
            clip = ImageClip(arr, duration=dur)
            clips.append(clip)

        # Concatenate all clips
        video = concatenate_videoclips(clips, method="compose")

        # Add audio if provided
        if audio_path and Path(audio_path).exists():
            try:
                audio = AudioFileClip(audio_path)
                # Trim audio to match video duration
                if audio.duration > video.duration:
                    audio = audio.subclipped(0, video.duration)
                video = video.with_audio(audio)
                logger.info(f"Added audio from {audio_path}")
            except Exception as e:
                logger.warning(f"Failed to add audio: {e}. Continuing without audio.")

        # Ensure output directory exists
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Export
        logger.info(f"Exporting video to {output_path}...")
        video.write_videofile(
            str(out_path),
            fps=VIDEO_FPS,
            codec=VIDEO_CODEC,
            audio_codec=AUDIO_CODEC if video.audio else None,
            preset="medium",
            threads=4,
            logger=None,  # suppress moviepy's verbose output
        )

        # Cleanup
        video.close()
        for clip in clips:
            clip.close()

        file_size_mb = out_path.stat().st_size / (1024 * 1024)
        logger.info(f"Video saved: {output_path} ({file_size_mb:.1f} MB)")

        return str(out_path)

    def _calculate_frame_durations(
        self,
        messages: List[Dict],
        total_frames: int,
        target_duration: Optional[float] = None,
    ) -> List[float]:
        """
        Calculate per-frame hold durations based on message delays.

        Frame mapping:
        - Frame 0 (empty chat): 0.5s
        - Frames 1..N-1: delay_ms from corresponding message / 1000
        - Frame N (final, all messages): 1.5s (hold for punchline)

        Durations are clamped between 0.8s and 3.5s, then
        optionally scaled to hit the target_duration.

        Args:
            messages: List of message dicts (with delay_ms).
            total_frames: Total number of frames.
            target_duration: Target total duration in seconds.

        Returns:
            List of float durations (one per frame).
        """
        durations = []

        for i in range(total_frames):
            if i == 0:
                # Empty chat frame
                durations.append(0.5)
            elif i == total_frames - 1:
                # Final frame — hold for punchline
                durations.append(1.5)
            else:
                # Message frames
                msg_idx = i - 1  # frame 1 corresponds to message 0
                if msg_idx < len(messages):
                    delay = messages[msg_idx].get("delay_ms", 1200) / 1000.0
                    # Clamp between 0.8 and 3.5 seconds
                    delay = max(0.8, min(3.5, delay))
                    durations.append(delay)
                else:
                    durations.append(1.2)

        # Scale to target duration if provided
        if target_duration and target_duration > 0:
            current_total = sum(durations)
            if current_total > 0:
                scale = target_duration / current_total
                durations = [d * scale for d in durations]
                # Re-clamp after scaling
                durations = [max(0.3, min(5.0, d)) for d in durations]

        return durations
