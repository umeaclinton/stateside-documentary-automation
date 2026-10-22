import logging
import os
from pathlib import Path
from typing import List, Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


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
                    f"Client secrets file not found: {client_secrets_file}. "
                    "Download it from Google Cloud Console (OAuth 2.0 Client ID) to enable uploads."
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


def upload_short_to_youtube(
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    client_secrets_file: str,
    token_file: str,
    privacy_status: str = "public",
    category_id: str = "27"  # 27 = Education, 22 = People & Blogs
) -> Dict:
    """
    Uploads a generated video to YouTube as a Short.
    Returns details including video ID and URL.
    """
    if not video_path.exists():
        raise FileNotFoundError(f"Video file to upload does not exist: {video_path}")

    # Ensure #Shorts is in the title for automatic YouTube Shorts categorization
    if "#Shorts" not in title and "#shorts" not in title:
        title = f"{title} #Shorts"

    youtube = get_authenticated_service(client_secrets_file, token_file)

    body = {
        "snippet": {
            "title": title[:100],  # YouTube title limit 100 chars
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
        chunksize=1024 * 1024 * 4,
        resumable=True
    )

    logger.info(f"Uploading '{title}' to YouTube ({privacy_status})...")
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
            logger.info(f"Upload progress: {progress}%")

    video_id = response.get("id")
    video_url = f"https://youtube.com/shorts/{video_id}"
    logger.info(f"Short published successfully! URL: {video_url}")

    return {
        "id": video_id,
        "url": video_url,
        "title": title,
        "status": privacy_status
    }
