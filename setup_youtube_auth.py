"""
One-Time YouTube OAuth Setup Assistant

Run this script locally once to connect your YouTube channel:
    python setup_youtube_auth.py

This will:
1. Open your browser for official Google OAuth authorization.
2. Generate 'oauth_token.json' with your channel's permanent refresh token.
3. Print the token string to copy-paste into GitHub Secrets for 24/7 cloud auto-posting.
"""

import json
import os
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

CLIENT_SECRET_FILE = Path("client_secret.json")
TOKEN_FILE = Path("oauth_token.json")


def main():
    print("=" * 65)
    print("🔑 YOUTUBE CHANNEL OAUTH SETUP ASSISTANT")
    print("=" * 65)

    if not CLIENT_SECRET_FILE.exists():
        print(f"\n❌ Error: '{CLIENT_SECRET_FILE}' not found in the project root!")
        print("\nHow to get client_secret.json:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com")
        print("2. Create a Project (or select an existing one).")
        print("3. Enable 'YouTube Data API v3' under APIs & Services > Library.")
        print("4. Go to APIs & Services > Credentials > Create Credentials > OAuth client ID.")
        print("5. Application Type: 'Desktop App'. Name it 'Shorts Uploader'.")
        print("6. Download the JSON file, rename it to 'client_secret.json', and save it in this directory.")
        sys.exit(1)

    print("\n🌐 Starting browser authentication flow...")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"\n✅ Authorization successful! Credentials saved to: {TOKEN_FILE.resolve()}")

    print("\n" + "=" * 65)
    print("📋 FOR GITHUB ACTIONS CLOUD AUTOMATION:")
    print("=" * 65)
    print("To let GitHub Actions upload to your YouTube channel automatically:")
    print("1. Go to your GitHub Repository > Settings > Secrets and variables > Actions.")
    print("2. Add new Repository Secret: 'YOUTUBE_CLIENT_SECRET_JSON'")
    print("   Value: (paste contents of client_secret.json)")
    print("3. Add new Repository Secret: 'YOUTUBE_OAUTH_TOKEN_JSON'")
    print("   Value: (paste the single-line token printed below)")
    print("-" * 65)
    print(creds.to_json())
    print("-" * 65)
    print("✅ Setup complete! You are ready to generate and post videos.\n")


if __name__ == "__main__":
    main()
