import json
import os
import sys
import re
import subprocess
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

CLIENT_SECRET_FILE = Path("client_secret.json")
TOKEN_FILE = Path("oauth_token.json")
AUTH_URL_FILE = Path("output/auth_url.txt")

# Intercept the generated auth URL to open Windows browser and write to disk
import builtins
_orig_print = builtins.print

def _intercept_print(*args, **kwargs):
    kwargs["flush"] = True
    _orig_print(*args, **kwargs)
    text = " ".join(str(a) for a in args)
    if "accounts.google.com" in text:
        match = re.search(r'(https://accounts\.google\.com[^\s]+)', text)
        if match:
            url = match.group(1)
            AUTH_URL_FILE.parent.mkdir(parents=True, exist_ok=True)
            AUTH_URL_FILE.write_text(url, encoding="utf-8")
            try:
                # Force Windows shell to open the user's active browser
                subprocess.Popen(f'start "" "{url}"', shell=True)
            except Exception:
                pass

builtins.print = _intercept_print

def main():
    print("=" * 65)
    print("[AUTH] YOUTUBE CHANNEL OAUTH SETUP ASSISTANT")
    print("=" * 65)

    if not CLIENT_SECRET_FILE.exists():
        print(f"\n[Error] '{CLIENT_SECRET_FILE}' not found in the project root!")
        sys.exit(1)

    print("\nStarting local authentication server on port 8080...")
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        SCOPES
    )
    
    # Run server on port 8080 (registered in desktop client)
    creds = flow.run_local_server(
        port=8080,
        authorization_prompt_message="Please visit this URL to authorize this application: {url}",
        success_message="Authorization complete! You may now close this window."
    )

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    print(f"\n[Success] Authorization successful! Credentials saved to: {TOKEN_FILE.resolve()}")

    print("\n" + "=" * 65)
    print("FOR GITHUB ACTIONS CLOUD AUTOMATION:")
    print("=" * 65)
    print("To let GitHub Actions upload to your YouTube channel automatically:")
    print("1. Go to your GitHub Repository > Settings > Secrets and variables > Actions.")
    print("2. Add new Repository Secret: 'YOUTUBE_CLIENT_SECRET_JSON'")
    print("   Value: (paste contents of client_secret.json)")
    print("3. Add new Repository Secret: 'YOUTUBE_OAUTH_TOKEN_JSON'")
    print("   Value: (paste contents of oauth_token.json)")
    print("=" * 65)
    print("[Success] Setup complete! You are ready to generate and post videos.\n")

if __name__ == "__main__":
    main()
