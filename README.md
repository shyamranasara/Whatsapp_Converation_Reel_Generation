# 🎬 WhatsApp Reel Generator

Generate **realistic WhatsApp conversation videos** in Hinglish (Hindi + English) for Instagram Reels, YouTube Shorts, and WhatsApp Status.

Give it a topic → it generates a funny, relatable conversation → renders pixel-accurate WhatsApp UI → exports a ready-to-post MP4 video.

---

## ✨ Features

- 🤖 **AI-Generated Conversations** — Powered by Google Gemini 1.5 Flash via LangChain
- 🎨 **Pixel-Accurate WhatsApp UI** — Dark & Light themes, blue ticks, typing indicator, avatars
- 🎭 **6 Preset Personas** — College boy, college girl, office uncle, desi mom, bhai type, sweet girlfriend
- 🎬 **MP4 Video Export** — 1080×1920 (9:16) at 30fps, H.264 encoded
- 🔊 **Optional Audio** — Notification sounds, typing sounds, gTTS narration
- 🖥️ **Streamlit Web UI** — Beautiful web interface for non-technical users
- ⌨️ **CLI Interface** — Full command-line support for automation

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- [FFmpeg](https://ffmpeg.org/download.html) installed and in PATH (required by MoviePy)
- A Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

### 2. Clone & Install

```bash
# Navigate to the project directory
cd whatsapp_reel_gen

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up API Key

```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. (Optional) Download Assets

For the best visual quality, download these fonts:

**NotoSans Font** (recommended for authentic WhatsApp look):
- Download from [Google Fonts - Noto Sans](https://fonts.google.com/noto/specimen/Noto+Sans)
- Place `NotoSans-Regular.ttf` in `assets/fonts/`

**Sound Effects** (optional):
- Place `notification.mp3` (WhatsApp notification sound) in `assets/sounds/`
- Place `typing.mp3` (typing indicator sound) in `assets/sounds/`
- Free sounds available at [Pixabay](https://pixabay.com/sound-effects/) or [Freesound](https://freesound.org/)

> **Note:** The app works without these assets — it falls back to system fonts and generates video without audio.

---

## 📖 Usage

### Streamlit Web UI

```bash
streamlit run app.py
```

This opens a beautiful web interface where you can:
1. Enter your topic and context
2. Select personas and duration
3. Click "Generate Reel"
4. Preview and download the video

### Command Line

```bash
python main.py \
  --topic "Priya ko Rahul ne anniversary bhool gayi" \
  --context "3 saal ho gaye, phir bhi bhool gaya, ek baar toh yaad rakh" \
  --duration 20 \
  --persona1 sweet_girlfriend \
  --persona2 college_boy \
  --theme dark \
  --output reel_001.mp4
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--topic` | Conversation topic (required) | — |
| `--context` | Additional scene context | "" |
| `--duration` | Video duration in seconds (5-30) | 15 |
| `--persona1` | First speaker persona | college_boy |
| `--persona2` | Second speaker persona | sweet_girlfriend |
| `--theme` | WhatsApp theme (dark/light) | dark |
| `--tone` | Conversation tone (dark_humor/funny/emotional) | dark_humor |
| `--output` | Output filename | auto-generated |
| `--temperature` | Gemini creativity (0.0-1.0) | 0.9 |
| `--api-key` | Override .env API key | — |
| `--verbose` | Enable debug logging | false |
| `--conversation-only` | Print JSON only (no video) | false |

### Available Personas

| Persona | Name | Style |
|---------|------|-------|
| `college_boy` | Rahul | Slang-heavy, meme-lover, deflects with humor |
| `college_girl` | Neha | Expressive, emoji-user, dramatic |
| `office_uncle` | Sharma Ji | Formal, gives unsolicited advice |
| `desi_mom` | Mummy | Guilt-trips, asks "khana khaya?" |
| `bhai_type` | Bunty | Ultra-casual, jugaad expert, fast typer |
| `sweet_girlfriend` | Priya | Caring but passive-aggressive when upset |

---

## 📁 Project Structure

```
whatsapp_reel_gen/
├── app.py                        # Streamlit web UI
├── main.py                       # CLI entry point
├── config.py                     # Settings, env loading, color palettes
├── requirements.txt
├── .env.example
├── assets/
│   ├── fonts/                    # Place NotoSans-Regular.ttf here
│   ├── sounds/                   # notification.mp3, typing.mp3
│   └── wallpapers/               # wa_bg_dark.png (optional)
├── src/
│   ├── conversation/
│   │   ├── generator.py          # Gemini conversation generation
│   │   ├── personas.py           # Character definitions
│   │   └── prompts.py            # LangChain prompt templates
│   ├── renderer/
│   │   ├── assets.py             # Font/avatar/wallpaper loader
│   │   ├── bubbles.py            # Chat bubble renderer
│   │   └── whatsapp_ui.py        # Full screen compositor
│   ├── video/
│   │   ├── animator.py           # PIL frames → MP4 video
│   │   └── audio.py              # Sound mixing
│   └── pipeline.py               # Main orchestration pipeline
└── output/                       # Generated videos appear here
```

---

## 🎬 Example Topics

```bash
# Couple fights
python main.py --topic "GF angry because BF liked ex's photo" --duration 20

# Friend group roasting
python main.py --topic "Group chat reaction when Bunty says 'I have a girlfriend'" \
  --persona1 bhai_type --persona2 college_boy --duration 25

# Desi mom vs kids
python main.py --topic "Mom found out about the hidden tattoo" \
  --persona1 desi_mom --persona2 college_girl --duration 20

# Office drama
python main.py --topic "Boss sends 'we need to talk' at 6 PM Friday" \
  --persona1 office_uncle --persona2 college_boy --duration 15
```

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `GOOGLE_API_KEY not set` | Create `.env` file with your API key |
| `FFmpeg not found` | Install FFmpeg and add to PATH |
| Video has no audio | Add sound files to `assets/sounds/` |
| Text looks wrong | Download NotoSans font to `assets/fonts/` |
| `JSON parse error` | The AI response was malformed. Try again — it retries once automatically |

---

## 📝 License

This project is for educational and personal use. Respect WhatsApp's branding guidelines when using generated content commercially.
