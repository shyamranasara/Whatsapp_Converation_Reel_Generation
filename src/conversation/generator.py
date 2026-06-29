"""
Conversation generator using Google Gemini via LangChain.

Generates realistic Hinglish WhatsApp conversations from a topic,
validates the JSON output, and adds realistic noise/imperfections.
"""

import json
import logging
import random
import re
from typing import Any, Dict, List, Optional

from langchain_google_genai import ChatGoogleGenerativeAI

from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, AVG_SECONDS_PER_MESSAGE
from src.conversation.personas import Persona
from src.conversation.prompts import build_conversation_prompt

logger = logging.getLogger(__name__)


class ConversationGenerator:
    """Generates WhatsApp-style conversations using Gemini."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """
        Initialize the generator with a Gemini API key.

        Args:
            api_key: Google API key for Gemini.
            model: Model name (default: gemini-1.5-flash or gemini-2.5-flash).
        """
        self.api_key = api_key
        self.model_name = model
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
        )

    def generate(
        self,
        topic: str,
        context: str,
        duration_seconds: int,
        p1_persona: Persona,
        p2_persona: Persona,
        relationship_type: str,
        family_mode: bool,
        humor_intensity: int,
        temperature: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Generate a conversation dict based on topic, context, and dynamic constraints.

        Args:
            topic: Conversation topic.
            context: Additional context/setup.
            duration_seconds: Target video duration in seconds.
            p1_persona: First persona spec.
            p2_persona: Second persona spec.
            relationship_type: The relationship (e.g. Couples, Friends, Boss-Employee).
            family_mode: If True, content will be wholesome; if False, clean adult roasts allowed.
            humor_intensity: Slider scale 1-10.
            temperature: Override temperature if specified.

        Returns:
            Validated conversation dict.
        """
        # Calculate target message count from duration
        message_count = max(4, int(duration_seconds / AVG_SECONDS_PER_MESSAGE))

        # Format persona traits as comma separated string
        p1_traits = ", ".join(p1_persona.specific_traits)
        p2_traits = ", ".join(p2_persona.specific_traits)

        # Build prompt using custom prompts template
        prompt = build_conversation_prompt(
            topic=topic,
            context=context,
            message_count=message_count,
            p1_name=p1_persona.name,
            p1_desc=p1_persona.personality_description,
            p1_traits=p1_traits,
            p2_name=p2_persona.name,
            p2_desc=p2_persona.personality_description,
            p2_traits=p2_traits,
            relationship_type=relationship_type,
            family_mode=family_mode,
            humor_intensity=humor_intensity,
        )

        if temperature is not None:
            self.llm.temperature = temperature

        chain = prompt | self.llm

        last_error = None
        for attempt in range(2):
            try:
                logger.info(f"Generating conversation (attempt {attempt + 1})...")
                response = chain.invoke({"topic": topic, "context": context})

                # Extract text content
                raw_text = response.content if hasattr(response, 'content') else str(response)
                logger.debug(f"Raw response length: {len(raw_text)} chars")

                # Parse and validate
                conversation = self._parse_json(raw_text)
                self._validate_schema(conversation)

                # Add realistic imperfections based on humor intensity
                conversation["messages"] = self._add_realistic_noise(
                    conversation["messages"],
                    humor_intensity=humor_intensity
                )

                # Attach persona metadata for the renderer
                conversation["_personas"] = {
                    "s1": {
                        "name": p1_persona.name,
                        "avatar_color": p1_persona.avatar_color,
                        "side": p1_persona.side,
                    },
                    "s2": {
                        "name": p2_persona.name,
                        "avatar_color": p2_persona.avatar_color,
                        "side": p2_persona.side,
                    },
                }

                logger.info(
                    f"Generated {len(conversation['messages'])} messages for topic: {topic}"
                )
                return conversation

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if self.model_name == "gemini-2.5-flash":
                    logger.info("Switching to fallback model: gemini-1.5-flash due to API error")
                    self.model_name = "gemini-1.5-flash"
                    self.llm = ChatGoogleGenerativeAI(
                        model=self.model_name,
                        google_api_key=self.api_key,
                        temperature=temperature or DEFAULT_TEMPERATURE,
                        top_p=DEFAULT_TOP_P,
                    )
                    chain = prompt | self.llm
                continue

        raise ValueError(
            f"Failed to generate valid conversation after 2 attempts. Last error: {last_error}"
        )

    def _parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Parse JSON from the model response, stripping markdown fences if present."""
        text = raw_text.strip()

        # Strip markdown code fences (```json ... ``` or ``` ... ```)
        fence_pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
        match = re.search(fence_pattern, text, re.DOTALL)
        if match:
            text = match.group(1).strip()

        return json.loads(text)

    def _validate_schema(self, data: Dict[str, Any]) -> None:
        """Validate that the conversation dict matches the expected schema."""
        if "speakers" not in data:
            raise ValueError("Missing 'speakers' in conversation JSON")
        if "messages" not in data:
            raise ValueError("Missing 'messages' in conversation JSON")

        speakers = data["speakers"]
        if not isinstance(speakers, list) or len(speakers) < 2:
            raise ValueError("'speakers' must be a list with at least 2 entries")

        speaker_ids = set()
        for sp in speakers:
            if "id" not in sp or "name" not in sp:
                raise ValueError(f"Speaker missing 'id' or 'name': {sp}")
            speaker_ids.add(sp["id"])

        messages = data["messages"]
        if not isinstance(messages, list) or len(messages) < 2:
            raise ValueError("'messages' must be a list with at least 2 entries")

        for msg in messages:
            required_keys = {"id", "speaker_id", "text", "timestamp"}
            missing = required_keys - set(msg.keys())
            if missing:
                raise ValueError(f"Message {msg.get('id', '?')} missing keys: {missing}")

            if msg["speaker_id"] not in speaker_ids:
                raise ValueError(
                    f"Message {msg['id']} has unknown speaker_id '{msg['speaker_id']}'"
                )

            if "delay_ms" not in msg:
                msg["delay_ms"] = random.randint(800, 2000)

            if "read" not in msg:
                msg["read"] = True

    def _add_realistic_noise(self, messages: List[Dict], humor_intensity: int = 5) -> List[Dict]:
        """
        Add realistic imperfections to make the conversation feel more human.
        Noise density scales with humor_intensity.
        """
        if len(messages) < 3:
            return messages

        # 1. Emoji reactions scaling with humor_intensity
        # Higher humor_intensity = more dramatic emojis
        emoji_reaction_prob = 0.3 + (humor_intensity * 0.05)  # 35% to 80% chance
        eligible = [m for m in messages if not m["text"].endswith(("😂", "💀", "🤣", "😭", "🙄", "🤦‍♂️"))]
        
        for msg in eligible:
            if random.random() < emoji_reaction_prob:
                if humor_intensity >= 8:
                    reaction = random.choice(["💀😭😂", "😭😭😭", "🤦‍♂️🤦‍♂️🤦‍♂️", "🙄🙄", "😡😡"])
                elif humor_intensity >= 4:
                    reaction = random.choice(["😂", "💀", "🤣", "😭"])
                else:
                    reaction = random.choice(["😊", "👍", "accha"])
                
                # Check for "accha" text vs emoji
                if reaction == "accha":
                    msg["text"] = msg["text"].rstrip() + " accha"
                else:
                    msg["text"] = msg["text"].rstrip() + " " + reaction

        # 2. Typos & corrections (higher frequency if humor_intensity is high)
        typo_prob = 0.2 + (humor_intensity * 0.03)  # 23% to 50%
        correction_candidates = [
            m for m in messages
            if len(m["text"]) > 10 and "*" not in m["text"]
        ]
        
        if correction_candidates and random.random() < typo_prob:
            msg = random.choice(correction_candidates)
            words = msg["text"].split()
            if len(words) >= 3:
                idx = random.randint(1, len(words) - 1)
                original_word = words[idx]
                # Filter out pure emoji words or short symbols
                if len(original_word) >= 3 and original_word.isalpha():
                    typo_idx = random.randint(0, len(original_word) - 2)
                    typo_word = (
                        original_word[:typo_idx]
                        + original_word[typo_idx + 1]
                        + original_word[typo_idx]
                        + original_word[typo_idx + 2:]
                    )
                    words[idx] = typo_word
                    msg["text"] = " ".join(words)

                    # Insert correction message right after
                    correction_msg = {
                        "id": msg["id"] + 900,
                        "speaker_id": msg["speaker_id"],
                        "text": f"{original_word}*",
                        "timestamp": msg["timestamp"],
                        "delay_ms": 600,
                        "read": msg.get("read", True),
                    }
                    msg_idx = messages.index(msg)
                    messages.insert(msg_idx + 1, correction_msg)

        # 3. Dynamic pause gaps ("...") before dramatic or long messages
        dots_prob = 0.15 + (humor_intensity * 0.02)
        for i in range(1, len(messages)):
            prev = messages[i - 1]
            curr = messages[i]
            if (
                prev["speaker_id"] != curr["speaker_id"]
                and len(curr["text"]) > 25
                and random.random() < dots_prob
            ):
                dots_msg = {
                    "id": curr["id"] + 800,
                    "speaker_id": curr["speaker_id"],
                    "text": "...",
                    "timestamp": curr["timestamp"],
                    "delay_ms": 800 + (humor_intensity * 100),
                    "read": True,
                }
                messages.insert(i, dots_msg)
                break

        # Re-sequence IDs
        for idx, msg in enumerate(messages, start=1):
            msg["id"] = idx

        return messages
