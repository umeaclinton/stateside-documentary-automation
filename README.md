# 🎬 Autonomous Zero-Cost YouTube Shorts Pipeline

An end-to-end, 100% free automated pipeline for generating, editing, captioning, and publishing viral, evergreen YouTube Shorts on autopilot.

No expensive SaaS subscriptions ($0 vs $50–$100/mo on FacelessReels / InVideo). No manual video editing. No high GPU requirements.

---

## 🏗️ Architecture & Free Stack

```text
       [ GitHub Actions (Free Cron Trigger: Daily 2:00 PM UTC) ]
                                  │
                                  ▼
      [ 1. SCRIPT GENERATION: Google Gemini API (100% Free) ]
          Writes high-retention hook, 3 rapid body points,
          psychological loop outro, and B-roll queries as structured JSON
                                  │
                                  ▼
     [ 2. NEURAL VOICEOVER: Microsoft Edge-TTS (100% Free) ]
          Generates ultra-realistic human speech (e.g. Christopher / Jenny)
          + word-accurate timestamp cues without token limits
                                  │
                                  ▼
     [ 3. B-ROLL FOOTAGE: Pexels Video API (100% Free) ]
          Downloads cinematic vertical 1080x1920 HD portrait clips
          matching scene keywords (20,000 free API calls/mo)
                                  │
                                  ▼
     [ 4. VIDEO COMPOSITOR: FFmpeg & Kinetic Subtitles ]
          Dynamic multi-scene cuts (~3.5s per scene), portrait crop,
          ducked background music, and bold kinetic animated captions
                                  │
                                  ▼
     [ 5. AUTONOMOUS PUBLISHING: YouTube Data API v3 (Free) ]
          Directly publishes to your channel with optimized title,
          description, tags, and #Shorts categorization
```

---

## 🌟 Evergreen High-RPM Niches (Won't Fade Over Time)

1. **Psychology & Human Behavior / Stoicism (Default)**
   - Examples: *"Dark Psychology Tricks in Conversation"*, *"Marcus Aurelius Stoic Rules"*, *"Signs Someone is Trying to Manipulate You"*.
   - **Why it works**: Generational appeal, high retention, timeless interest.
2. **Financial Literacy & High-Income Career Skills**
   - Examples: *"3 High-Paying Skills You Can Learn in 30 Days"*, *"How Top 1% People Negotiate"*.
   - **Why it works**: Huge YouTube CPM/RPM ($8–$20 per thousand views) and direct synergy with professional audiences.
3. **Deep Science & Ancient Mysteries**
   - Examples: *"The Paradox That Breaks Modern Physics"*, *"The Lost Civilization Before Egypt"*.
   - **Why it works**: High curiosity, visually striking B-roll.

---

## 🚀 Quickstart (Local Test)

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone <your-repo-url>
cd "YT video automation"

# Create virtual environment & install dependencies
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in:
- `GEMINI_API_KEY`: Get free key from [Google AI Studio](https://aistudio.google.com).
- `PEXELS_API_KEY`: Get free key from [Pexels API](https://www.pexels.com/api/).

### 3. Generate a Test Short (Without Uploading)
```bash
python main.py --skip-upload --topic "The psychological trick to win any argument with silence"
```
Your rendered video, audio, script, and subtitles will appear inside the `output/run_<timestamp>/` directory!

---

## 🔑 YouTube API Setup (One-Time)

To enable automatic posting:
1. Go to [Google Cloud Console](https://console.cloud.google.com).
2. Create a project and enable the **YouTube Data API v3**.
3. Go to **APIs & Services > Credentials > Create Credentials > OAuth client ID**.
4. Choose Application Type: **Desktop App**.
5. Download the credentials file and save it as `client_secret.json` in this project folder.
6. Run the authentication script:
   ```bash
   python setup_youtube_auth.py
   ```
   A browser window will open. Sign in to your YouTube channel and grant permission. This will generate your permanent `oauth_token.json`.

---

## ☁️ 24/7 Cloud Autopilot (GitHub Actions)

You don't need your computer running! The GitHub Actions workflow executes on GitHub's free multi-core cloud servers on a schedule.

### Step 1: Push Project to GitHub
```bash
git init
git add .
git commit -m "feat: complete zero-cost YouTube Shorts automation engine"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

### Step 2: Add GitHub Repository Secrets
Go to your repository on GitHub: **Settings > Secrets and variables > Actions > New repository secret**.

Add the following 4 secrets:
1. `GEMINI_API_KEY`: Your Gemini API key.
2. `PEXELS_API_KEY`: Your Pexels API key.
3. `YOUTUBE_CLIENT_SECRET_JSON`: The entire text contents of your `client_secret.json`.
4. `YOUTUBE_OAUTH_TOKEN_JSON`: The entire text contents of your generated `oauth_token.json`.

### Step 3: Enjoy Automated Posting!
- **Scheduled**: Runs automatically every day at 14:00 UTC (customizable in `.github/workflows/generate_and_post.yml`).
- **Manual Trigger**: Go to the **Actions** tab on GitHub, click **YouTube Shorts Auto-Pilot Pipeline**, and click **Run workflow** anytime to generate and post on demand!
