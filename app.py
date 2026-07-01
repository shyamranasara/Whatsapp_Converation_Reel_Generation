"""
Streamlit UI for WhatsApp Reel Generator.

A rich web interface for generating WhatsApp conversation reels
with real-time preview and download capabilities.
"""

import json
import logging
import os
import threading
import time
import streamlit as st

from src.conversation.personas import list_persona_names, PERSONA_PRESETS
from src.pipeline import ReelPipeline

def schedule_file_deletion(file_path: str, delay: int = 300):
    """Schedules the deletion of a generated video file after a delay in seconds."""
    def delete_job():
        time.sleep(delay)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logging.getLogger("app").info(f"Auto-deleted video after {delay}s: {file_path}")
        except Exception as e:
            logging.getLogger("app").warning(f"Failed to auto-delete {file_path}: {e}")

    threading.Thread(target=delete_job, daemon=True).start()

def cleanup_old_videos():
    """Runs a quick cleanup of any old reels in the output directory."""
    from config import OUTPUT_DIR
    try:
        if OUTPUT_DIR.exists():
            for f in OUTPUT_DIR.glob("*.mp4"):
                if time.time() - os.path.getmtime(f) > 300:
                    os.remove(f)
                    logging.getLogger("app").info(f"Cleaned up stale video: {f}")
    except Exception as e:
        logging.getLogger("app").warning(f"Failed to run startup cleanup: {e}")

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="WhatsApp Reel Generator",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for premium look
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    /* Dark theme overrides */
    .stApp {
        background-color: #0B141A;
    }
    
    /* Header styling */
    h1 {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
    }
    
    /* Card styling */
    .css-1r6slb0, .css-12w0qpk {
        background-color: #202C33;
        border-radius: 12px;
        padding: 16px;
    }
    
    /* Button styling */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background-color: #111B21;
    }
    
    /* Success message */
    .stSuccess {
        background-color: #005C4B;
        border-color: #25D366;
    }
    
    /* Persona cards */
    .persona-card {
        background: #202C33;
        border-radius: 8px;
        padding: 12px;
        margin: 4px 0;
        border-left: 4px solid #25D366;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Suppress noisy loggers
for noisy in ["PIL", "moviepy", "urllib3", "httpcore", "httpx"]:
    logging.getLogger(noisy).setLevel(logging.WARNING)

# Run cleanup of stale videos on startup
cleanup_old_videos()

# Load API key from env as default
from config import GOOGLE_API_KEY
GOOGLE_API_KEY_SEC = GOOGLE_API_KEY
api_key = GOOGLE_API_KEY_SEC

# ---------------------------------------------------------------------------
# Sidebar — Settings
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    
    theme = st.radio(
        "Theme",
        options=["dark", "light"],
        index=0,
        horizontal=True,
        help="WhatsApp color theme for the reel",
    )
    
    st.divider()
    
    st.markdown("### 🎭 Behavior Control")
    
    family_mode = st.checkbox(
        "Family Mode",
        value=False,
        help="If checked, strictly wholesome/clean content. If unchecked, clean adult humor/desi roasts allowed.",
    )
    
    humor_intensity = st.slider(
        "Humor Intensity (1–10)",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        help="1 = subtle/mundane, 10 = chaotic roasting/maximum drama.",
    )
    
    relationship_type = st.selectbox(
        "Relationship Type",
        options=["Friends", "Couples", "Parent-Child", "Boss-Employee", "Toxic Exes"],
        index=0,
        help="Contextualizes how the characters interact with each other.",
    )
    
    st.divider()
    
    st.markdown("### 🔧 Advanced")
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.9,
        step=0.05,
        help="Higher = more creative/random. Lower = more predictable.",
    )
    
    st.divider()
    st.markdown(
        "**Built with** ❤️ using Gemini AI + LangChain + MoviePy"
    )

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("🎬 WhatsApp Reel Generator")
st.markdown(
    "Generate realistic WhatsApp conversation reels in Hinglish. "
    "Perfect for Instagram Reels, YouTube Shorts, and WhatsApp Status."
)

st.divider()

# Input columns
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### 💬 Conversation Setup")
    
    topic = st.text_input(
        "Topic / Scenario",
        placeholder="Couple ka jhagda over dinner plans",
        help="What's the conversation about?",
    )
    
    context = st.text_area(
        "Situation Context (Details)",
        placeholder="Priya wants to go to a fancy restaurant, Rahul is broke this month but can't say it directly.",
        help="Set the scene — what's the situation? More detail = funnier output.",
        height=120,
    )

with col2:
    st.markdown("### 🎭 Characters & Duration")
    
    persona_names = list_persona_names()
    persona_display = {
        name: f"{PERSONA_PRESETS[name].name} ({name.replace('_', ' ').title()})"
        for name in persona_names
    }
    
    duration = st.slider(
        "Reel Duration (seconds)",
        min_value=5,
        max_value=30,
        value=15,
        help="5-30 seconds. Instagram Reels sweet spot is 15-20s.",
    )
    
    st.markdown("---")
    
    p1_col, p2_col = st.columns(2)
    
    with p1_col:
        st.markdown("#### 👤 Character 1 (Right Side)")
        p1_custom = st.checkbox("Custom Profile 1", value=False, key="p1_custom")
        if p1_custom:
            p1_name = st.text_input("Name", value="Rahul", key="p1_custom_name")
            p1_preset_base = st.selectbox(
                "Preset Base",
                options=persona_names,
                index=0,
                format_func=lambda x: persona_display.get(x, x),
                key="p1_custom_preset_base",
            )
            base_p1 = PERSONA_PRESETS[p1_preset_base]
            p1_desc = st.text_area("Core Personality", value=base_p1.personality_description, key="p1_custom_desc", height=80)
            p1_traits_str = st.text_input(
                "Traits (comma-separated)",
                value=", ".join(base_p1.specific_traits),
                key="p1_custom_traits",
            )
            
            # Premium customization controls
            hex_color_p1 = '#%02x%02x%02x' % base_p1.avatar_color
            p1_color_hex = st.color_picker("Avatar Color", value=hex_color_p1, key="p1_custom_color")
            p1_color = tuple(int(p1_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            p1_speed = st.slider("Typing Delay (ms)", 400, 4000, value=int(base_p1.typing_speed_ms), step=100, key="p1_custom_speed")
            p1_emoji = st.selectbox("Emoji Frequency", options=["low", "medium", "high"], index=["low", "medium", "high"].index(base_p1.emoji_frequency), key="p1_custom_emoji")
            
            if st.button("💾 Save Character 1 as Preset", key="save_p1_btn"):
                persona_key = p1_name.lower().strip().replace(" ", "_")
                if not persona_key:
                    st.error("Name cannot be empty!")
                else:
                    from src.conversation.personas import save_custom_persona, Persona
                    traits_list = [t.strip() for t in p1_traits_str.split(",") if t.strip()]
                    new_p = Persona(
                        name=p1_name,
                        avatar_color=p1_color,
                        side="right",
                        typing_speed_ms=p1_speed,
                        emoji_frequency=p1_emoji,
                        personality_description=p1_desc,
                        specific_traits=traits_list,
                    )
                    save_custom_persona(persona_key, new_p)
                    st.success(f"Character '{p1_name}' saved successfully! You can now select it in presets.")
                    st.rerun()

            p1_config = {
                "is_custom": True,
                "name": p1_name,
                "preset_base": p1_preset_base,
                "custom_traits": p1_traits_str,
                "personality_description": p1_desc,
                "avatar_color": p1_color,
                "typing_speed_ms": p1_speed,
                "emoji_frequency": p1_emoji,
            }
        else:
            p1_preset = st.selectbox(
                "Preset Profile",
                options=persona_names,
                index=persona_names.index("college_boy") if "college_boy" in persona_names else 0,
                format_func=lambda x: persona_display.get(x, x),
                key="p1_preset_select",
            )
            p1 = PERSONA_PRESETS[p1_preset]
            st.caption(f"*{p1.personality_description}*")
            st.caption(f"Traits: {', '.join(p1.specific_traits)}")
            p1_config = {
                "is_custom": False,
                "preset": p1_preset,
            }
    
    with p2_col:
        st.markdown("#### 👤 Character 2 (Left Side)")
        p2_custom = st.checkbox("Custom Profile 2", value=False, key="p2_custom")
        if p2_custom:
            p2_name = st.text_input("Name", value="Priya", key="p2_custom_name")
            p2_preset_base = st.selectbox(
                "Preset Base",
                options=persona_names,
                index=1,
                format_func=lambda x: persona_display.get(x, x),
                key="p2_custom_preset_base",
            )
            base_p2 = PERSONA_PRESETS[p2_preset_base]
            p2_desc = st.text_area("Core Personality", value=base_p2.personality_description, key="p2_custom_desc", height=80)
            p2_traits_str = st.text_input(
                "Traits (comma-separated)",
                value=", ".join(base_p2.specific_traits),
                key="p2_custom_traits",
            )
            
            # Premium customization controls
            hex_color_p2 = '#%02x%02x%02x' % base_p2.avatar_color
            p2_color_hex = st.color_picker("Avatar Color", value=hex_color_p2, key="p2_custom_color")
            p2_color = tuple(int(p2_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            p2_speed = st.slider("Typing Delay (ms)", 400, 4000, value=int(base_p2.typing_speed_ms), step=100, key="p2_custom_speed")
            p2_emoji = st.selectbox("Emoji Frequency", options=["low", "medium", "high"], index=["low", "medium", "high"].index(base_p2.emoji_frequency), key="p2_custom_emoji")
            
            if st.button("💾 Save Character 2 as Preset", key="save_p2_btn"):
                persona_key = p2_name.lower().strip().replace(" ", "_")
                if not persona_key:
                    st.error("Name cannot be empty!")
                else:
                    from src.conversation.personas import save_custom_persona, Persona
                    traits_list = [t.strip() for t in p2_traits_str.split(",") if t.strip()]
                    new_p = Persona(
                        name=p2_name,
                        avatar_color=p2_color,
                        side="left",
                        typing_speed_ms=p2_speed,
                        emoji_frequency=p2_emoji,
                        personality_description=p2_desc,
                        specific_traits=traits_list,
                    )
                    save_custom_persona(persona_key, new_p)
                    st.success(f"Character '{p2_name}' saved successfully! You can now select it in presets.")
                    st.rerun()

            p2_config = {
                "is_custom": True,
                "name": p2_name,
                "preset_base": p2_preset_base,
                "custom_traits": p2_traits_str,
                "personality_description": p2_desc,
                "avatar_color": p2_color,
                "typing_speed_ms": p2_speed,
                "emoji_frequency": p2_emoji,
            }
        else:
            p2_preset = st.selectbox(
                "Preset Profile",
                options=persona_names,
                index=persona_names.index("sweet_girlfriend") if "sweet_girlfriend" in persona_names else 1,
                format_func=lambda x: persona_display.get(x, x),
                key="p2_preset_select",
            )
            p2 = PERSONA_PRESETS[p2_preset]
            st.caption(f"*{p2.personality_description}*")
            st.caption(f"Traits: {', '.join(p2.specific_traits)}")
            p2_config = {
                "is_custom": False,
                "preset": p2_preset,
            }

st.divider()

# ---------------------------------------------------------------------------
# Generate button and flow
# ---------------------------------------------------------------------------
gen_col, preview_col = st.columns([1, 1])

with gen_col:
    generate_clicked = st.button(
        "🚀 Generate Reel",
        type="primary",
        use_container_width=True,
        disabled=not topic,
    )

if generate_clicked:
    
    if not topic:
        st.error("⚠️ Please enter a topic for the conversation.")
        st.stop()
    
    progress = st.progress(0, text="Initializing pipeline...")
    status = st.empty()
    
    try:
        # Step 1: Initialize
        status.info("🔧 Setting up pipeline...")
        progress.progress(10, text="Initializing...")
        pipeline = ReelPipeline(api_key=GOOGLE_API_KEY_SEC)
        
        # Step 2: Generate conversation
        status.info("🤖 Generating conversation with Gemini AI...")
        progress.progress(25, text="Generating conversation...")
        
        conversation = pipeline.generate_conversation_only(
            topic=topic,
            context=context,
            duration_seconds=duration,
            p1_config=p1_config,
            p2_config=p2_config,
            relationship_type=relationship_type,
            family_mode=family_mode,
            humor_intensity=humor_intensity,
            temperature=temperature,
        )
        
        # Show conversation preview
        with st.expander("📝 Generated Conversation (Preview)", expanded=True):
            for msg in conversation.get("messages", []):
                speaker_name = "Unknown"
                for sp in conversation.get("speakers", []):
                    if sp["id"] == msg["speaker_id"]:
                        speaker_name = sp["name"]
                        break
                st.markdown(f"**{speaker_name}** ({msg['timestamp']}): {msg['text']}")
        
        # Step 3: Render frames
        status.info("🎨 Rendering WhatsApp frames...")
        progress.progress(50, text="Rendering frames...")
        
        from src.renderer.whatsapp_ui import WhatsAppRenderer
        renderer = WhatsAppRenderer(theme=theme)
        frames = renderer.render_all_frames(conversation)
        
        # Step 4: Create video
        status.info("🎬 Animating video...")
        progress.progress(75, text="Creating video...")
        
        from src.video.animator import VideoAnimator
        animator = VideoAnimator()
        
        import time
        output_filename = f"reel_{int(time.time())}.mp4"
        from config import OUTPUT_DIR
        output_path = str(OUTPUT_DIR / output_filename)
        
        result_path = animator.create_video(
            frames=frames,
            conversation=conversation,
            output_path=output_path,
            target_duration=float(duration),
        )
        
        progress.progress(100, text="Done!")
        status.empty()
        
        # Success!
        st.success("✅ Reel generated successfully!")
        
        # Video preview
        st.markdown("### 🎥 Your Reel")
        st.video(result_path)
        
        # Download button
        with open(result_path, 'rb') as f:
            video_bytes = f.read()
        
        # Auto-delete file on disk after 5 minutes to save storage space
        schedule_file_deletion(result_path, delay=300)
        
        st.download_button(
            label="⬇️ Download MP4",
            data=video_bytes,
            file_name="whatsapp_reel.mp4",
            mime="video/mp4",
            use_container_width=True,
        )
        
        # Stats
        import os
        file_size = os.path.getsize(result_path) / (1024 * 1024)
        msg_count = len(conversation.get("messages", []))
        
        stat1, stat2, stat3 = st.columns(3)
        stat1.metric("Messages", msg_count)
        stat2.metric("Duration", f"{duration}s")
        stat3.metric("File Size", f"{file_size:.1f} MB")
    
    except ValueError as e:
        progress.empty()
        status.empty()
        st.error(f"❌ Configuration Error: {e}")
    
    except RuntimeError as e:
        progress.empty()
        status.empty()
        st.error(f"❌ Runtime Error: {e}")
    
    except Exception as e:
        progress.empty()
        status.empty()
        st.error(f"❌ Unexpected Error: {e}")
        logging.getLogger("app").error(f"Pipeline failed: {e}", exc_info=True)

# ---------------------------------------------------------------------------
# Footer with tips
# ---------------------------------------------------------------------------
st.divider()
with st.expander("💡 Tips for better reels"):
    st.markdown("""
    **Topic ideas that go viral:**
    - Couple fights over small things (dinner plans, replying late, forgetting anniversaries)
    - Group chat roasting someone who's in a new relationship
    - Desi mom vs. modern kids conversations
    - Office politics and boss-employee drama
    - Friend asking for money they owe
    - Planning a trip that never happens
    
    **Context matters:**
    The more specific your context, the funnier the output. Instead of "couple fight", try:
    "Priya wants to go to a fancy restaurant for their 3rd anniversary, but Rahul just spent his salary on a PS5 and hasn't told her yet"
    
    **Duration tips:**
    - **5-10s**: Quick punchline, 4-5 messages
    - **15-20s**: Full scenario, 6-8 messages (Instagram Reels sweet spot)
    - **25-30s**: Extended drama, 10-12 messages
    """)
