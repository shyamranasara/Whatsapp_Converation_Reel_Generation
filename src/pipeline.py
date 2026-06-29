"""
Main pipeline — orchestrates conversation generation, rendering, and video export.

This is the core entry point that wires all modules together:
1. Load/build custom personas
2. Generate conversation via Gemini
3. Render WhatsApp UI frames
4. Mix audio (optional)
5. Animate frames into MP4 video
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, Optional

from config import GOOGLE_API_KEY, OUTPUT_DIR
from src.conversation.generator import ConversationGenerator
from src.conversation.personas import Persona, get_persona, build_custom_persona
from src.renderer.whatsapp_ui import WhatsAppRenderer
from src.video.animator import VideoAnimator
from src.video.audio import AudioMixer

logger = logging.getLogger(__name__)


class ReelPipeline:
    """End-to-end pipeline for generating WhatsApp reel videos."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the pipeline.

        Args:
            api_key: Google API key. Falls back to GOOGLE_API_KEY env var.
        """
        self.api_key = api_key or GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError(
                "No API key provided. Set GOOGLE_API_KEY in .env or pass api_key parameter."
            )

        self.generator = ConversationGenerator(self.api_key)
        self.animator = VideoAnimator()
        self.audio_mixer = AudioMixer()

    def run(
        self,
        topic: str,
        context: str = "",
        duration_seconds: int = 15,
        p1_config: Optional[Dict[str, Any]] = None,
        p2_config: Optional[Dict[str, Any]] = None,
        relationship_type: str = "Friends",
        family_mode: bool = False,
        humor_intensity: int = 5,
        theme: str = "dark",
        output_filename: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Run the full reel generation pipeline.

        Args:
            topic: Conversation topic.
            context: Additional context.
            duration_seconds: Target video duration.
            p1_config: Config dictionary for persona 1.
            p2_config: Config dictionary for persona 2.
            relationship_type: Relationship context.
            family_mode: Wholesome toggle.
            humor_intensity: Sarcasm slider (1-10).
            theme: Dark / Light theme.
            output_filename: Custom output filename.
            temperature: Gemini temperature override.
        """
        start_time = time.time()

        # ------------------------------------------------------------------
        # Step 1: Load / build personas
        # ------------------------------------------------------------------
        logger.info("Resolving speaker personas...")
        persona1 = self._resolve_persona(p1_config, default_preset="college_boy", side="right")
        persona2 = self._resolve_persona(p2_config, default_preset="sweet_girlfriend", side="left")

        # Ensure personas are on opposite sides
        if persona1.side == persona2.side:
            persona2.side = "left" if persona1.side == "right" else "right"

        logger.info(
            f"Persona 1: {persona1.name} ({persona1.side}) - Traits: {persona1.specific_traits}, "
            f"Persona 2: {persona2.name} ({persona2.side}) - Traits: {persona2.specific_traits}"
        )

        # ------------------------------------------------------------------
        # Step 2: Generate conversation
        # ------------------------------------------------------------------
        logger.info(f"Generating conversation. Theme: {theme}, Relationship: {relationship_type}")
        conversation = self.generator.generate(
            topic=topic,
            context=context,
            duration_seconds=duration_seconds,
            p1_persona=persona1,
            p2_persona=persona2,
            relationship_type=relationship_type,
            family_mode=family_mode,
            humor_intensity=humor_intensity,
            temperature=temperature,
        )

        msg_count = len(conversation.get("messages", []))
        logger.info(f"Generated {msg_count} messages")

        # ------------------------------------------------------------------
        # Step 3: Render frames
        # ------------------------------------------------------------------
        logger.info(f"Rendering frames with '{theme}' theme...")
        renderer = WhatsAppRenderer(theme=theme)
        frames = renderer.render_all_frames(conversation)
        logger.info(f"Rendered {len(frames)} frames")

        # ------------------------------------------------------------------
        # Step 4: Mix audio (optional)
        # ------------------------------------------------------------------
        audio_path = None
        if self.audio_mixer.has_sounds:
            logger.info("Mixing audio...")
            message_times = self._calculate_message_times(conversation, len(frames))
            total_duration = sum(
                self.animator._calculate_frame_durations(
                    conversation.get("messages", []),
                    len(frames),
                    float(duration_seconds),
                )
            )
            audio_output = str(OUTPUT_DIR / "temp_audio.mp3")
            audio_path = self.audio_mixer.create_mixed_audio(
                message_times, total_duration, audio_output
            )
        else:
            logger.info("No sound files available. Creating video without audio.")

        # ------------------------------------------------------------------
        # Step 5: Create video
        # ------------------------------------------------------------------
        if output_filename is None:
            timestamp = int(time.time())
            output_filename = f"reel_{timestamp}.mp4"

        output_path = str(OUTPUT_DIR / output_filename)

        logger.info(f"Creating video: {output_path}")
        try:
            result_path = self.animator.create_video(
                frames=frames,
                conversation=conversation,
                output_path=output_path,
                audio_path=audio_path,
                target_duration=float(duration_seconds),
            )
        except Exception as e:
            logger.error(f"Video creation failed: {e}")
            raise RuntimeError(f"Video export failed: {e}") from e

        # Cleanup temp audio
        temp_audio = OUTPUT_DIR / "temp_audio.mp3"
        if temp_audio.exists():
            try:
                temp_audio.unlink()
            except Exception:
                pass

        elapsed = time.time() - start_time
        logger.info(
            f"Pipeline complete in {elapsed:.1f}s. Output: {result_path}"
        )

        return result_path

    def _resolve_persona(
        self,
        config: Optional[Dict[str, Any]],
        default_preset: str,
        side: str,
    ) -> Persona:
        """Helper to build a Persona from dynamic config options."""
        if not config:
            p = get_persona(default_preset)
            p.side = side
            return p

        # Check if they just passed preset name or preset key
        preset_name = config.get("preset") or config.get("preset_base") or default_preset
        is_custom = config.get("is_custom", False)

        if not is_custom:
            p = get_persona(preset_name)
            p.side = side
            return p

        name = config.get("name") or config.get("custom_name") or "User"
        custom_traits = config.get("custom_traits") or []
        if isinstance(custom_traits, str):
            custom_traits = [t.strip() for t in custom_traits.split(",") if t.strip()]

        desc = config.get("personality_description") or config.get("desc")

        p = build_custom_persona(
            name=name,
            side=side,
            preset_base=preset_name,
            custom_traits=custom_traits,
            personality_description=desc,
        )
        return p

    def _calculate_message_times(
        self,
        conversation: Dict[str, Any],
        total_frames: int,
    ) -> list:
        """Calculate the timestamp (in seconds) when each message appears."""
        messages = conversation.get("messages", [])
        durations = self.animator._calculate_frame_durations(
            messages, total_frames
        )

        times = []
        current_time = 0.0
        for i, dur in enumerate(durations):
            if i > 0:  # skip frame 0 (empty chat)
                times.append(current_time)
            current_time += dur

        return times[:len(messages)]

    def generate_conversation_only(
        self,
        topic: str,
        context: str = "",
        duration_seconds: int = 15,
        p1_config: Optional[Dict[str, Any]] = None,
        p2_config: Optional[Dict[str, Any]] = None,
        relationship_type: str = "Friends",
        family_mode: bool = False,
        humor_intensity: int = 5,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate just the conversation JSON without rendering video.
        Useful for previewing / debugging.
        """
        persona1 = self._resolve_persona(p1_config, default_preset="college_boy", side="right")
        persona2 = self._resolve_persona(p2_config, default_preset="sweet_girlfriend", side="left")

        if persona1.side == persona2.side:
            persona2.side = "left" if persona1.side == "right" else "right"

        return self.generator.generate(
            topic=topic,
            context=context,
            duration_seconds=duration_seconds,
            p1_persona=persona1,
            p2_persona=persona2,
            relationship_type=relationship_type,
            family_mode=family_mode,
            humor_intensity=humor_intensity,
            temperature=temperature,
        )
