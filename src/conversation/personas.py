"""
Persona definitions for WhatsApp conversation characters.

Each persona encapsulates personality traits that influence how
the AI generates dialogue and how the renderer styles messages.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import json
from pathlib import Path
from config import BASE_DIR


@dataclass
class Persona:
    """Represents a single WhatsApp chat participant."""

    name: str
    avatar_color: Tuple[int, int, int]  # RGB
    side: str  # "left" (receiver) or "right" (sender)
    typing_speed_ms: int  # delay before this person's message appears (800-2000)
    emoji_frequency: str  # "low" | "medium" | "high"
    personality_description: str  # personality blurb fed into the prompt
    specific_traits: List[str] = field(default_factory=list)

    def __post_init__(self):
        assert self.side in ("left", "right"), f"side must be 'left' or 'right', got '{self.side}'"
        assert 400 <= self.typing_speed_ms <= 4000, "typing_speed_ms out of range"
        assert self.emoji_frequency in ("low", "medium", "high")


# ---------------------------------------------------------------------------
# Preset persona templates
# ---------------------------------------------------------------------------

PERSONA_PRESETS: Dict[str, Persona] = {
    "college_boy": Persona(
        name="Rahul",
        avatar_color=(55, 135, 195),   # blue
        side="right",
        typing_speed_ms=900,
        emoji_frequency="medium",
        personality_description=(
            "A 21-year-old college boy who loves memes, avoids deep emotional "
            "conversations, and deflects serious topics with casual humor."
        ),
        specific_traits=["funny", "sarcastic", "lazy", "pubg-addict"],
    ),
    "college_girl": Persona(
        name="Neha",
        avatar_color=(220, 100, 150),  # pink
        side="left",
        typing_speed_ms=1100,
        emoji_frequency="high",
        personality_description=(
            "A 20-year-old college girl who is highly expressive, dramatic, "
            "asks many questions, and mixes Hindi and English naturally."
        ),
        specific_traits=["expressive", "dramatic", "talkative", "Hinglish-pro"],
    ),
    "office_uncle": Persona(
        name="Sharma Ji",
        avatar_color=(120, 90, 60),    # brown
        side="left",
        typing_speed_ms=1800,
        emoji_frequency="low",
        personality_description=(
            "A 45-year-old office uncle who types slowly with proper punctuation, "
            "gives unsolicited life advice, and loves forwarding WhatsApp wisdom."
        ),
        specific_traits=["formal", "preachy", "boomer-energy", "punctual"],
    ),
    "desi_mom": Persona(
        name="Mummy",
        avatar_color=(180, 80, 80),    # warm red
        side="left",
        typing_speed_ms=2000,
        emoji_frequency="low",
        personality_description=(
            "A typical Indian mother who writes like she talks, asks about food "
            "constantly, and guilt-trips naturally."
        ),
        specific_traits=["caring", "guilt-trip-expert", "food-obsessed", "religious"],
    ),
    "bhai_type": Persona(
        name="Bunty",
        avatar_color=(80, 180, 80),    # green
        side="right",
        typing_speed_ms=800,
        emoji_frequency="medium",
        personality_description=(
            "A local tapori/bhai style friend who replies in rapid fragments, "
            "always knows a 'jugaad', and is fiercely loyal but rough around the edges."
        ),
        specific_traits=["tapori-slang", "street-smart", "hyperactive", "loyal"],
    ),
    "sweet_girlfriend": Persona(
        name="Priya",
        avatar_color=(200, 130, 200),  # lavender
        side="left",
        typing_speed_ms=1200,
        emoji_frequency="high",
        personality_description=(
            "A sweet but passive-aggressive girlfriend who remembers everything "
            "and goes from warm to passive-aggressive quickly when upset."
        ),
        specific_traits=["romantic", "passive-aggressive", "possessive", "sharp-tongued"],
    ),
}

CUSTOM_PERSONAS_FILE = BASE_DIR / "custom_personas.json"

def load_custom_personas() -> Dict[str, Persona]:
    """Load custom personas from custom_personas.json."""
    custom = {}
    if CUSTOM_PERSONAS_FILE.exists():
        try:
            with open(CUSTOM_PERSONAS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, val in data.items():
                    custom[key] = Persona(
                        name=val["name"],
                        avatar_color=tuple(val["avatar_color"]),
                        side=val.get("side", "left"),
                        typing_speed_ms=val.get("typing_speed_ms", 1000),
                        emoji_frequency=val.get("emoji_frequency", "medium"),
                        personality_description=val["personality_description"],
                        specific_traits=val.get("specific_traits", []),
                    )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to load custom personas: {e}")
    return custom


def save_custom_persona(key: str, persona: Persona):
    """Save a custom persona to the JSON file and register in-memory."""
    custom_data = {}
    if CUSTOM_PERSONAS_FILE.exists():
        try:
            with open(CUSTOM_PERSONAS_FILE, "r", encoding="utf-8") as f:
                custom_data = json.load(f)
        except Exception:
            pass
            
    custom_data[key] = {
        "name": persona.name,
        "avatar_color": list(persona.avatar_color),
        "side": persona.side,
        "typing_speed_ms": persona.typing_speed_ms,
        "emoji_frequency": persona.emoji_frequency,
        "personality_description": persona.personality_description,
        "specific_traits": persona.specific_traits,
    }
    
    try:
        CUSTOM_PERSONAS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CUSTOM_PERSONAS_FILE, "w", encoding="utf-8") as f:
            json.dump(custom_data, f, indent=4, ensure_ascii=False)
        PERSONA_PRESETS[key] = persona
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Failed to save custom persona: {e}")


# Load custom personas initially
try:
    for _k, _p in load_custom_personas().items():
        PERSONA_PRESETS[_k] = _p
except Exception:
    pass


def get_persona(preset_name: str) -> Persona:
    """
    Retrieve a preset persona by name.

    Args:
        preset_name: One of the keys in PERSONA_PRESETS.

    Returns:
        A copy of the Persona so callers can mutate safely.
    """
    key = preset_name.lower().strip()
    if key not in PERSONA_PRESETS:
        available = ", ".join(sorted(PERSONA_PRESETS.keys()))
        raise ValueError(
            f"Unknown persona '{preset_name}'. Available: {available}"
        )
    original = PERSONA_PRESETS[key]
    return Persona(
        name=original.name,
        avatar_color=original.avatar_color,
        side=original.side,
        typing_speed_ms=original.typing_speed_ms,
        emoji_frequency=original.emoji_frequency,
        personality_description=original.personality_description,
        specific_traits=original.specific_traits.copy(),
    )


def list_persona_names() -> list:
    """Return sorted list of available persona preset names."""
    return sorted(PERSONA_PRESETS.keys())


def build_custom_persona(
    name: str,
    side: str,
    preset_base: Optional[str] = None,
    custom_traits: Optional[List[str]] = None,
    personality_description: Optional[str] = None,
    avatar_color: Optional[Tuple[int, int, int]] = None,
    typing_speed_ms: Optional[int] = None,
    emoji_frequency: Optional[str] = None,
) -> Persona:
    """
    Dynamically generates a custom Persona profile.

    Args:
        name: Name of the character.
        side: "left" or "right".
        preset_base: Optional name of the preset to base the persona on.
        custom_traits: List of custom traits to add or merge.
        personality_description: Optional custom core personality text.
        avatar_color: Optional custom avatar color tuple.
        typing_speed_ms: Optional typing speed delay.
        emoji_frequency: Optional emoji frequency.
    """
    if preset_base:
        try:
            base = get_persona(preset_base)
        except ValueError:
            base = None
    else:
        base = None

    if base:
        traits = base.specific_traits.copy()
        if custom_traits:
            for t in custom_traits:
                t_clean = t.strip()
                if t_clean and t_clean not in traits:
                    traits.append(t_clean)
        return Persona(
            name=name,
            avatar_color=avatar_color or base.avatar_color,
            side=side,
            typing_speed_ms=typing_speed_ms or base.typing_speed_ms,
            emoji_frequency=emoji_frequency or base.emoji_frequency,
            personality_description=personality_description or base.personality_description,
            specific_traits=traits,
        )
    else:
        traits = [t.strip() for t in custom_traits if t.strip()] if custom_traits else ["Normal", "Desi"]
        return Persona(
            name=name,
            avatar_color=avatar_color or (100, 100, 100),  # default grey
            side=side,
            typing_speed_ms=typing_speed_ms or 1200,
            emoji_frequency=emoji_frequency or "medium",
            personality_description=personality_description or f"A custom character named {name}.",
            specific_traits=traits,
        )
