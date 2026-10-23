"""
Automated Voice Cloning Assistant

Usage:
1. Record 1 to 2 minutes of yourself talking clearly (phone voice memo or microphone).
2. Save the audio file into: assets/voice_samples/my_voice.mp3 (or .wav, .m4a)
3. Run:
    python clone_my_voice.py --file assets/voice_samples/my_voice.mp3 --name "My Personal Voice"

This script will:
- Send your voice sample to ElevenLabs.
- Train your custom instant Voice Clone.
- Retrieve your unique Voice ID.
- Automatically save ELEVENLABS_VOICE_ID into your .env and credentials vault!
"""

import argparse
import os
import sys
from pathlib import Path
import requests
from dotenv import load_dotenv, set_key

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
VAULT_PATH = BASE_DIR / "credentials" / "credentials_vault.md"

load_dotenv(ENV_PATH)


def clone_voice(audio_file_path: Path, voice_name: str):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("\n❌ Error: ELEVENLABS_API_KEY is not set in your .env file!")
        print("1. Go to https://elevenlabs.io and sign up for a free account.")
        print("2. Click your profile icon at the bottom left > Profile + API Key > Copy API Key.")
        print("3. Paste it into your .env file as: ELEVENLABS_API_KEY=your_key_here\n")
        sys.exit(1)

    if not audio_file_path.exists():
        print(f"\n❌ Error: Audio sample file not found: {audio_file_path}")
        print("Please place your voice recording (MP3/WAV/M4A) in assets/voice_samples/ and try again.\n")
        sys.exit(1)

    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {"xi-api-key": api_key}
    data = {
        "name": voice_name,
        "description": "Custom cloned voice for automated YouTube Shorts",
    }

    print(f"🎙️ Uploading '{audio_file_path.name}' to ElevenLabs to clone your voice...")
    with open(audio_file_path, "rb") as f:
        files = [("files", (audio_file_path.name, f, "audio/mpeg"))]
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=60)

    if resp.status_code != 200:
        print(f"\n❌ Voice cloning failed ({resp.status_code}): {resp.text}\n")
        sys.exit(1)

    voice_id = resp.json().get("voice_id")
    print(f"\n🎉 SUCCESS! Your voice was cloned successfully!")
    print(f"🆔 Voice ID: {voice_id}")

    # Save to .env
    set_key(str(ENV_PATH), "ELEVENLABS_VOICE_ID", voice_id)
    print(f"✅ Saved ELEVENLABS_VOICE_ID to {ENV_PATH}")

    # Append to credentials vault
    if VAULT_PATH.exists():
        content = VAULT_PATH.read_text(encoding="utf-8")
        if "## 4. ElevenLabs Voice Cloning" not in content:
            new_section = f"\n---\n\n## 4. ElevenLabs Voice Cloning\n* **API Key:** `{api_key}`\n* **Voice ID:** `{voice_id}`\n* **Voice Name:** `{voice_name}`\n* **Purpose:** Custom personal voice clone for voiceovers.\n"
            VAULT_PATH.write_text(content + new_section, encoding="utf-8")
            print(f"✅ Updated credentials vault: {VAULT_PATH}")

    print("\n🚀 Ready! Future video generations will now speak in your exact voice!\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Instant Voice Cloning Helper")
    parser.add_argument("--file", type=str, default="assets/voice_samples/my_voice.mp3", help="Path to your audio voice recording")
    parser.add_argument("--name", type=str, default="My Personal Voice", help="Label for your cloned voice")
    args = parser.parse_args()

    clone_voice(Path(args.file), args.name)
