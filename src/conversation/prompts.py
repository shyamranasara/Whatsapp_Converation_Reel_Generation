"""
Prompt templates for the Gemini conversation generator.

Uses LangChain ChatPromptTemplate to build structured prompts
with Hinglish style instructions, tone guidelines, and few-shot examples.
"""

from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

# ---------------------------------------------------------------------------
# System prompt template
# ---------------------------------------------------------------------------
SYSTEM_TEMPLATE = """You are a realistic WhatsApp conversation writer for Indian audiences.

YOUR TASK:
Generate a realistic WhatsApp conversation in Hinglish (Hindi + English mix) based on the following:
- Topic: {topic}
- Context: {context}
- Relationship Type: {relationship_type}
- Family Mode Toggle: {family_mode}
- Humor Intensity (1-10 Slider): {humor_intensity}

SPEAKER PROFILES:
- Person 1 (id: "s1"): Name: {p1_name}, Personality Base: {p1_desc}, Specific Traits: {p1_traits}
- Person 2 (id: "s2"): Name: {p2_name}, Personality Base: {p2_desc}, Specific Traits: {p2_traits}

ENGINE RULES & SAFETY:
- If Family Mode is True:
  * Keep content 100% wholesome, clean, and family-friendly.
  * No swearing, double entendres, spicy slang, or edgy roasts.
  * Focus on sweet, funny everyday domestic/family situations.
- If Family Mode is False (clean adult humor / desi burns / gaali_allowed):
  * Set gaali_allowed=True.
  * You can use mild/soft street-level Hinglish burns/slang ("saala", "kameena", "dramebaaz", "ullu ka pattha", "shut up yaar").
  * Absolutely NO hard abusive, sexual, or highly offensive words.

HUMOR INTENSITY (1 to 10):
- Low (1-3): Slower pacing, realistic mundane chatter, gentle teasing, light/soft punchline.
- Medium (4-7): Sarcastic comebacks, active roasting, natural desi slang, sharp punchline.
- High (8-10): Chaotic roasting, maximum drama, fast pacing, highly absurd arguments, very sharp punchlines/callbacks.

CONVERSATION RULES:
1. Every message bubble must be SHORT — 1 to 2 sentences max. Real people never write paragraphs on WhatsApp.
2. Use Hinglish naturally (e.g. "yaar", "bhai", "matlab", "accha", "bas", "chill kar", "kya scene hai", "relatable hai", "sach bata", "arrey").
3. Use emojis realistically (only 30-40% of messages). Real people don't emoji-spam.
4. Alternate speaker_id, but occasionally a speaker can send 2 consecutive messages (rapid fire texting).
5. The last message must deliver a sharp punchline or callback to the opening topic.
6. Return ONLY raw JSON matching the JSON schema below. Do not wrap in markdown ```json blocks.

JSON SCHEMA:
{{
  "topic": "string — topic of the conversation",
  "speakers": [
    {{"id": "s1", "name": "{p1_name}"}},
    {{"id": "s2", "name": "{p2_name}"}}
  ],
  "messages": [
    {{
      "id": 1,
      "speaker_id": "s1",
      "text": "message text here",
      "timestamp": "HH:MM AM/PM",
      "delay_ms": 1200,
      "read": true
    }}
  ]
}}

RULES FOR MESSAGES ARRAY:
- Generate exactly {message_count} messages.
- delay_ms: time before this message appears. Range 800-3000. First message = 500.
- timestamp: realistic time increments, each message 0-2 minutes after the previous.
- read: true for all messages, except optionally the last message (which can be false to show unread status).
"""

# ---------------------------------------------------------------------------
# Few-shot examples
# ---------------------------------------------------------------------------
FEW_SHOT_TOXIC_ROAST = """
--- FEW-SHOT EXAMPLE 1: Toxic Relationship Roast (Family Mode = False, Humor Intensity = 9) ---
TOPIC: "Boyfriend forgot anniversary"
OUTPUT:
{
  "topic": "Boyfriend forgot anniversary",
  "speakers": [
    {"id": "s1", "name": "Priya"},
    {"id": "s2", "name": "Rahul"}
  ],
  "messages": [
    {"id": 1, "speaker_id": "s1", "text": "Happy anniversary Rahul! 💖", "timestamp": "10:00 AM", "delay_ms": 500, "read": true},
    {"id": 2, "speaker_id": "s1", "text": "Reply toh kar saala... 1 ghanta ho gaya", "timestamp": "11:05 AM", "delay_ms": 1200, "read": true},
    {"id": 3, "speaker_id": "s2", "text": "Arrey happy anniversary yaarr! Sorry, game mein tha 😅", "timestamp": "11:06 AM", "delay_ms": 1500, "read": true},
    {"id": 4, "speaker_id": "s1", "text": "Game? Anniversary pe PUBG khel raha hai?", "timestamp": "11:07 AM", "delay_ms": 800, "read": true},
    {"id": 5, "speaker_id": "s1", "text": "Kameene thodi toh sharm kar le 🙂", "timestamp": "11:07 AM", "delay_ms": 600, "read": true},
    {"id": 6, "speaker_id": "s2", "text": "Arrey baby drop pe level 3 bag mila tha, kaise chhodta? 😭", "timestamp": "11:08 AM", "delay_ms": 1800, "read": true},
    {"id": 7, "speaker_id": "s1", "text": "Accha! Toh ab level 3 bag se hi shaadi kar lo, go get married to Bunty. Bye.", "timestamp": "11:09 AM", "delay_ms": 1000, "read": false}
  ]
}
"""

FEW_SHOT_CLEAN_FAMILY = """
--- FEW-SHOT EXAMPLE 2: Wholesome Family Conversation (Family Mode = True, Humor Intensity = 4) ---
TOPIC: "Getting dhaniya from market"
OUTPUT:
{
  "topic": "Getting dhaniya from market",
  "speakers": [
    {"id": "s1", "name": "Mummy"},
    {"id": "s2", "name": "Rohan"}
  ],
  "messages": [
    {"id": 1, "speaker_id": "s1", "text": "Rohan, market mein ho kya?", "timestamp": "5:30 PM", "delay_ms": 500, "read": true},
    {"id": 2, "speaker_id": "s2", "text": "Haan mummy, bolo. Kuch chahiye?", "timestamp": "5:31 PM", "delay_ms": 1000, "read": true},
    {"id": 3, "speaker_id": "s1", "text": "Aloo le aana, aur dhaniya mat bhoolna. Free mein maang lena bhaiya se.", "timestamp": "5:32 PM", "delay_ms": 1400, "read": true},
    {"id": 4, "speaker_id": "s2", "text": "Mummy free mein koi nahi deta aajkal... 🤦‍♂️", "timestamp": "5:33 PM", "delay_ms": 900, "read": true},
    {"id": 5, "speaker_id": "s1", "text": "Mujhe mat sikhao! Main hoti toh poori tokri le aati. Bas aaloo ke paise dena.", "timestamp": "5:34 PM", "delay_ms": 2000, "read": true},
    {"id": 6, "speaker_id": "s2", "text": "Theek hai mummy, main chalta hoon, varna shopkeeper mujhe bhaga dega.", "timestamp": "5:35 PM", "delay_ms": 1100, "read": false}
  ]
}
"""

# ---------------------------------------------------------------------------
# Human message template (the actual user request)
# ---------------------------------------------------------------------------
HUMAN_TEMPLATE = """Generate a WhatsApp conversation for:

TOPIC: {topic}
CONTEXT: {context}

Remember: Output ONLY the JSON. No other text."""


def build_conversation_prompt(
    topic: str,
    context: str,
    message_count: int,
    p1_name: str,
    p1_desc: str,
    p1_traits: str,
    p2_name: str,
    p2_desc: str,
    p2_traits: str,
    relationship_type: str,
    family_mode: bool,
    humor_intensity: int,
) -> ChatPromptTemplate:
    """
    Build the full LangChain prompt for conversation generation.
    """
    system_text = SYSTEM_TEMPLATE.format(
        topic=topic,
        context=context,
        relationship_type=relationship_type,
        family_mode="True (Wholesome, absolutely clean)" if family_mode else "False (Edgy burns allowed)",
        humor_intensity=humor_intensity,
        p1_name=p1_name,
        p1_desc=p1_desc,
        p1_traits=p1_traits,
        p2_name=p2_name,
        p2_desc=p2_desc,
        p2_traits=p2_traits,
        message_count=message_count,
    )

    # Append relevant few-shot examples
    full_system = system_text + "\n\n" + FEW_SHOT_TOXIC_ROAST + "\n\n" + FEW_SHOT_CLEAN_FAMILY

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=full_system),
        HumanMessagePromptTemplate.from_template(
            HUMAN_TEMPLATE,
            input_variables=["topic", "context"],
        ),
    ])

    return prompt
