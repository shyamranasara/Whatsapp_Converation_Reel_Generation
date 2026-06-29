# WhatsApp Reel Generator — Free Deployment Guide

This guide details how to deploy the **WhatsApp Reel Generator** web application (Streamlit UI) online **100% free of cost**.

---

## 📋 Prerequisites
Before deploying to any platform:
1. **GitHub Repository**: Push your code to a public or private GitHub repository.
2. **Google API Key**: Get a free API key from the [Google AI Studio](https://aistudio.google.com/apikey).
3. **Environment Files**: Make sure `.env` is listed in your `.gitignore` so your API keys are never pushed publicly.

---

## 🚀 Option 1: Streamlit Community Cloud (Recommended)
This is the easiest and most native way to host your Streamlit application for free.

### Setup Steps:
1. Sign up/Log in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click the **"New app"** button.
3. Select your GitHub repository, the branch (e.g., `main`), and the main file path: `app.py`.
4. Click **"Deploy!"**.

### System Dependencies:
Streamlit Community Cloud reads [packages.txt](file:///c:/Users/r_ran/Desktop/Shyam/Projects/Reel Generater/Whatsapp_Converation/packages.txt) automatically on startup and installs `ffmpeg` (required by MoviePy for video rendering).

### Adding your Google API Key:
1. Once deployed, click the **Settings** menu at the bottom right of your app page.
2. Go to **Secrets**.
3. Add your key in TOML format:
   ```toml
   GOOGLE_API_KEY = "AIzaSy..."
   ```
4. Save. Streamlit will restart the app and read the secret automatically!

---

## 🤗 Option 2: Hugging Face Spaces (High Resources)
Hugging Face offers free hosting for Streamlit applications with up to **16 GB RAM** and a very stable environment.

### Setup Steps:
1. Sign up/Log in to [Hugging Face](https://huggingface.co/).
2. Go to **Spaces** and click **"Create new Space"**.
3. Fill in the details:
   - **Space Name**: e.g., `whatsapp-reel-generator`
   - **License**: e.g., `mit`
   - **SDK**: Select **Streamlit**.
   - **Space Hardware**: Select the **Free CPU Basic** tier (16GB RAM).
   - **Visibility**: Public or Private.
4. Click **"Create Space"**.
5. Clone the space repository locally or upload your files directly to the Space via web upload/Git.
   - *Note: Ensure your code has the `requirements.txt` and `packages.txt` files in the root.*

### Adding your Google API Key:
1. Inside your Space, click on the **Settings** tab at the top.
2. Scroll down to the **Variables and secrets** section.
3. Click **"New secret"**:
   - **Name**: `GOOGLE_API_KEY`
   - **Value**: Your Google Gemini API Key.
4. Hugging Face will automatically load this secret into Python's environment variables (`os.environ`), and your app's `config.py` will read it natively!

---

## 📦 Option 3: Render (Python Web Service)
Render is a cloud provider that allows hosting Python apps, but has a slower cold start on the free tier.

### Setup Steps:
1. Sign up/Log in to [Render](https://render.com/).
2. Click **"New +"** and choose **"Web Service"**.
3. Connect your GitHub repository.
4. Configure the settings:
   - **Name**: `whatsapp-reel-generator`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Select the **Free** instance type.

### System Dependencies (FFmpeg):
To install FFmpeg on Render, add a Buildpack or configure a custom shell script:
1. Go to the **Settings** tab in Render.
2. Add a Custom Environment Variable:
   - **Key**: `YUM_PACKAGES` or `APT_PACKAGES`
   - **Value**: `ffmpeg`
3. Alternately, configure deployment via a custom `Dockerfile` containing:
   ```dockerfile
   FROM python:3.10-slim
   RUN apt-get update && apt-get install -y ffmpeg
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   CMD ["python", "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
   ```

### Adding your Google API Key:
1. In the service settings, click on the **Environment** tab.
2. Click **"Add Environment Variable"**:
   - **Key**: `GOOGLE_API_KEY`
   - **Value**: Your API key.
3. Save changes.
