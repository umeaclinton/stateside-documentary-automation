import logging
import re
from pathlib import Path
from typing import List, Optional
import requests

logger = logging.getLogger(__name__)

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def _sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-_.]', '_', name)


def fetch_broll_clip(
    api_key: str,
    query: str,
    output_dir: Path,
    min_duration: float = 3.0
) -> Optional[Path]:
    """
    Searches Pexels API for a vertical portrait video clip matching the query,
    and downloads it to output_dir.
    """
    if not api_key:
        logger.warning("PEXELS_API_KEY not set. Skipping B-roll download.")
        return None

    headers = {
        "Authorization": api_key,
        "User-Agent": "YouTubeShortsAutomation/1.0"
    }

    params = {
        "query": query,
        "orientation": "portrait",
        "per_page": 8,
        "size": "medium"
    }

    try:
        response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        videos = data.get("videos", [])

        if not videos:
            # Fallback to broader query if specific query yields nothing
            logger.info(f"No direct videos for '{query}'. Trying fallback 'dark cinematic'...")
            params["query"] = "dark cinematic mood"
            fallback_resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
            videos = fallback_resp.json().get("videos", [])

        if not videos:
            logger.warning(f"No Pexels videos found for query '{query}'")
            return None

        # Iterate through videos to find the best portrait HD file
        for video in videos:
            video_id = video.get("id")
            video_files = video.get("video_files", [])
            
            # Prefer 1080x1920 (HD portrait) or any portrait file with height > width
            chosen_file = None
            
            # Priority 1: Exact 1080x1920
            for vf in video_files:
                if vf.get("width") == 1080 and vf.get("height") == 1920 and vf.get("file_type") == "video/mp4":
                    chosen_file = vf
                    break

            # Priority 2: Any portrait HD file (height > width)
            if not chosen_file:
                for vf in video_files:
                    w = vf.get("width", 0) or 0
                    h = vf.get("height", 0) or 0
                    if h > w and vf.get("file_type") == "video/mp4":
                        chosen_file = vf
                        break

            # Priority 3: First available mp4
            if not chosen_file and video_files:
                chosen_file = video_files[0]

            if not chosen_file or not chosen_file.get("link"):
                continue

            download_url = chosen_file["link"]
            file_name = f"broll_{video_id}_{_sanitize_filename(query)[:30]}.mp4"
            dest_path = output_dir / file_name

            # Skip download if already cached
            if dest_path.exists() and dest_path.stat().st_size > 50000:
                logger.info(f"Using cached B-roll clip: {dest_path.name}")
                return dest_path

            # Download video stream
            logger.info(f"Downloading B-roll for '{query}' from Pexels (ID: {video_id})...")
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                logger.info(f"Successfully downloaded clip to: {dest_path}")
                return dest_path

        return None

    except Exception as e:
        logger.error(f"Error fetching B-roll from Pexels: {e}")
        return None


def fetch_all_broll_clips(
    api_key: str,
    keywords_list: List[str],
    output_dir: Path
) -> List[Path]:
    """
    Downloads B-roll clips for a list of keyword prompts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    clips: List[Path] = []

    for kw in keywords_list:
        clip_path = fetch_broll_clip(api_key, kw, output_dir)
        if clip_path and clip_path.exists():
            clips.append(clip_path)

    return clips
