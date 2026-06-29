"""
CLI entry point for WhatsApp Reel Generator.

Usage:
    python main.py \
        --topic "Priya ko Rahul ne anniversary bhool gayi" \
        --context "3 saal ho gaye, phir bhi bhool gaya" \
        --duration 20 \
        --persona1 sweet_girlfriend \
        --persona2 college_boy \
        --relationship-type Couples \
        --humor-intensity 8 \
        --theme dark \
        --output output/reel_001.mp4
"""

import argparse
import logging
import sys

from src.conversation.personas import list_persona_names
from src.pipeline import ReelPipeline


def main():
    """Parse arguments and run the reel generation pipeline."""
    # Ensure console output supports Unicode emojis without crashing on Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    persona_choices = list_persona_names()

    parser = argparse.ArgumentParser(
        description="WhatsApp Reel Generator - Create realistic WhatsApp conversation reels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available personas: {', '.join(persona_choices)}

Example:
  python main.py \\
    --topic "Priya ko Rahul ne anniversary bhool gayi" \\
    --context "3 saal ho gaye, phir bhi bhool gaya, ek baar toh yaad rakh" \\
    --duration 20 \\
    --persona1 sweet_girlfriend \\
    --persona2 college_boy \\
    --relationship-type Couples \\
    --humor-intensity 8 \\
    --theme dark
        """,
    )

    parser.add_argument(
        "--topic",
        type=str,
        required=True,
        help="Conversation topic / scenario (e.g., 'Couple ka jhagda over dinner plans')",
    )
    parser.add_argument(
        "--context",
        type=str,
        default="",
        help="Additional context for the conversation",
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=15,
        choices=range(5, 31),
        metavar="5-30",
        help="Reel duration in seconds (default: 15)",
    )
    parser.add_argument(
        "--persona1",
        type=str,
        default="college_boy",
        choices=persona_choices,
        help="Persona for speaker 1 (default: college_boy)",
    )
    parser.add_argument(
        "--persona2",
        type=str,
        default="sweet_girlfriend",
        choices=persona_choices,
        help="Persona for speaker 2 (default: sweet_girlfriend)",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default="dark",
        choices=["dark", "light"],
        help="WhatsApp theme (default: dark)",
    )
    parser.add_argument(
        "--family-mode",
        action="store_true",
        help="Enable strict family mode (wholesome only)",
    )
    parser.add_argument(
        "--humor-intensity",
        type=int,
        default=5,
        choices=range(1, 11),
        help="Humor intensity scale 1-10 (default: 5)",
    )
    parser.add_argument(
        "--relationship-type",
        type=str,
        default="Friends",
        choices=["Friends", "Couples", "Parent-Child", "Boss-Employee", "Toxic Exes"],
        help="Relationship type (default: Friends)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file path (default: output/reel_<timestamp>.mp4)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Override Gemini temperature (0.0-1.0)",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="Google API key (overrides .env)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--conversation-only",
        action="store_true",
        help="Only generate and print the conversation JSON (no video)",
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # Suppress noisy loggers
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("moviepy").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logger = logging.getLogger("main")

    try:
        logger.info("[*] WhatsApp Reel Generator")
        logger.info(f"   Topic: {args.topic}")
        logger.info(f"   Duration: {args.duration}s")
        logger.info(f"   Personas: {args.persona1} vs {args.persona2}")
        logger.info(f"   Theme: {args.theme}")
        logger.info(f"   Relationship: {args.relationship_type}")
        logger.info(f"   Family Mode: {args.family_mode}")
        logger.info(f"   Humor Intensity: {args.humor_intensity}")

        pipeline = ReelPipeline(api_key=args.api_key)

        p1_config = {"is_custom": False, "preset": args.persona1}
        p2_config = {"is_custom": False, "preset": args.persona2}

        if args.conversation_only:
            import json
            conversation = pipeline.generate_conversation_only(
                topic=args.topic,
                context=args.context,
                duration_seconds=args.duration,
                p1_config=p1_config,
                p2_config=p2_config,
                relationship_type=args.relationship_type,
                family_mode=args.family_mode,
                humor_intensity=args.humor_intensity,
                temperature=args.temperature,
            )
            print(json.dumps(conversation, indent=2, ensure_ascii=False))
            return

        output_path = pipeline.run(
            topic=args.topic,
            context=args.context,
            duration_seconds=args.duration,
            p1_config=p1_config,
            p2_config=p2_config,
            relationship_type=args.relationship_type,
            family_mode=args.family_mode,
            humor_intensity=args.humor_intensity,
            theme=args.theme,
            output_filename=args.output,
            temperature=args.temperature,
        )

        logger.info(f"[OK] Reel generated successfully: {output_path}")
        print(f"\nYour reel is ready: {output_path}")

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except RuntimeError as e:
        logger.error(f"Runtime error: {e}")
        sys.exit(2)
    except KeyboardInterrupt:
        logger.info("Cancelled by user.")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
