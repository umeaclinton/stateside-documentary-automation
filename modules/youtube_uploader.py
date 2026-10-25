import logging
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

# Scopes required to upload videos and set thumbnails
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube"
]

def get_authenticated_service(
    client_secrets_file: str,
    token_file: str
):
    """
    Handles YouTube Data API OAuth 2.0 authorization.
    Stores and reuses refresh tokens from token_file.
    """
    creds = None
    token_path = Path(token_file)

    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        except Exception as e:
            logger.warning(f"Error loading existing credentials from {token_file}: {e}")

    # If no valid credentials, refresh or prompt user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing expired YouTube OAuth credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(
                    f"Client secrets file not found: {client_secrets_file}.\n"
                    "Please download it from Google Cloud Console (OAuth 2.0 Client ID) to enable uploads."
                )
            logger.info("Initiating browser authentication flow for YouTube...")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for future unattended runs
        token_path.parent.mkdir(parents=True, exist_ok=True)
        with open(token_path, "w", encoding="utf-8") as token_out:
            token_out.write(creds.to_json())
        logger.info(f"Saved OAuth credentials to {token_file}")

    return build("youtube", "v3", credentials=creds)


def upload_video_essay_to_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    client_secrets_file: str,
    token_file: str,
    thumbnail_path: Optional[Path] = None,
    privacy_status: str = "public",
    category_id: str = "28"  # 28 = Science & Technology, 27 = Education
) -> Dict:
    """
    Uploads a long-form 16:9 documentary video essay to YouTube with custom thumbnail and tags.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file to upload does not exist: {video_path}")

    youtube = get_authenticated_service(client_secrets_file, token_file)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
        }
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        chunksize=1024 * 1024 * 8, # 8MB chunks for faster long-form upload
        resumable=True
    )

    print(f"\n[YouTube Upload] Uploading '{title}' to YouTube ({privacy_status})...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            print(f"  -> Upload progress: {progress}%")

    video_id = response.get("id")
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[Success] Video published successfully! URL: {video_url}")

    # Set custom high-CTR thumbnail if provided
    if thumbnail_path and thumbnail_path.exists():
        try:
            print(f"[YouTube Upload] Uploading custom cover thumbnail: {thumbnail_path.name}...")
            thumb_media = MediaFileUpload(str(thumbnail_path), mimetype="image/png")
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=thumb_media
            ).execute()
            print("  -> Custom thumbnail uploaded and attached successfully!")
        except Exception as e:
            print(f"  [Warning] Failed to set custom thumbnail: {e}")

    return {
        "id": video_id,
        "url": video_url,
        "title": title,
        "status": privacy_status
    }
