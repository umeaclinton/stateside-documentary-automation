import logging
import re
from pathlib import Path
from typing import List, Optional
import requests

logger = logging.getLogger(__name__)

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"
PIXABAY_SEARCH_URL = "https://pixabay.com/api/videos/"


def _sanitize_filename(name: str) -> str:
    return re.sub(r'[^\w\-_.]', '_', name)


def fetch_from_pixabay(
    api_key: str,
    query: str,
    output_dir: Path
) -> Optional[Path]:
    """
    Searches Pixabay API for high quality video matching query and downloads it.
    Pixabay API keys are instant, free, and have no waitlist.
    """
    if not api_key:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "key": api_key,
        "q": query,
        "video_type": "all",
        "per_page": 8,
        "safesearch": "true"
    }

    try:
        response = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        hits = data.get("hits", [])

        if not hits:
            # Try broader mood query
            params["q"] = "cinematic mood"
            fallback_resp = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=15)
            hits = fallback_resp.json().get("hits", [])

        if not hits:
            return None

        # Choose the best video hit
        for hit in hits:
            hit_id = hit.get("id")
            videos = hit.get("videos", {})
            
            # Prefer 'medium' or 'large' video stream
            chosen_stream = videos.get("large") or videos.get("medium") or videos.get("small")
            if not chosen_stream or not chosen_stream.get("url"):
                continue

            download_url = chosen_stream["url"]
            file_name = f"pixabay_{hit_id}_{_sanitize_filename(query)[:25]}.mp4"
            dest_path = output_dir / file_name

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                logger.info(f"Using cached Pixabay clip: {dest_path.name}")
                return dest_path

            logger.info(f"Downloading B-roll for '{query}' from Pixabay (ID: {hit_id})...")
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                logger.info(f"Successfully downloaded Pixabay clip: {dest_path.name}")
                return dest_path

        return None
    except Exception as e:
        logger.error(f"Error fetching from Pixabay: {e}")
        return None


def fetch_from_pexels(
    api_key: str,
    query: str,
    output_dir: Path
) -> Optional[Path]:
    """
    Searches Pexels API for vertical video clips.
    """
    if not api_key:
        return None

    output_dir.mkdir(parents=True, exist_ok=True)

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
        videos = response.json().get("videos", [])

        if not videos:
            params["query"] = "dark cinematic mood"
            fallback_resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
            videos = fallback_resp.json().get("videos", [])

        if not videos:
            return None

        for video in videos:
            video_id = video.get("id")
            video_files = video.get("video_files", [])
            chosen_file = None

            # Look for 1080x1920 or portrait
            for vf in video_files:
                if vf.get("width") == 1080 and vf.get("height") == 1920 and vf.get("file_type") == "video/mp4":
                    chosen_file = vf
                    break

            if not chosen_file:
                for vf in video_files:
                    if (vf.get("height", 0) or 0) > (vf.get("width", 0) or 0) and vf.get("file_type") == "video/mp4":
                        chosen_file = vf
                        break

            if not chosen_file and video_files:
                chosen_file = video_files[0]

            if not chosen_file or not chosen_file.get("link"):
                continue

            dest_path = output_dir / f"pexels_{video_id}_{_sanitize_filename(query)[:25]}.mp4"
            if dest_path.exists() and dest_path.stat().st_size > 50000:
                return dest_path

            logger.info(f"Downloading B-roll for '{query}' from Pexels (ID: {video_id})...")
            with requests.get(chosen_file["link"], stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                return dest_path

        return None
    except Exception as e:
        logger.error(f"Error fetching from Pexels: {e}")
        return None


def fetch_broll_clip(
    pexels_key: str,
    pixabay_key: str,
    query: str,
    output_dir: Path
) -> Optional[Path]:
    """
    Fetches B-roll from Pixabay or Pexels depending on which keys are configured.
    """
    # Try Pixabay first if key is present
    if pixabay_key:
        clip = fetch_from_pixabay(pixabay_key, query, output_dir)
        if clip:
            return clip

    # Try Pexels if key is present
    if pexels_key:
        clip = fetch_from_pexels(pexels_key, query, output_dir)
        if clip:
            return clip

    return None


def fetch_all_broll_clips(
    pexels_key: str,
    pixabay_key: str,
    keywords_list: List[str],
    output_dir: Path
) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    clips: List[Path] = []

    for kw in keywords_list:
        clip_path = fetch_broll_clip(pexels_key, pixabay_key, kw, output_dir)
        if clip_path and clip_path.exists():
            clips.append(clip_path)

    return clips
