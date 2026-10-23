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
    output_dir: Path,
    limit: int = 2
) -> List[Path]:
    """
    Searches Pixabay API for high quality videos matching query and downloads up to `limit` clips.
    """
    if not api_key:
        return []

    output_dir.mkdir(parents=True, exist_ok=True)

    params = {
        "key": api_key,
        "q": query,
        "video_type": "all",
        "per_page": 12,
        "safesearch": "true"
    }

    downloaded = []
    try:
        response = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=15)
        response.raise_for_status()
        hits = response.json().get("hits", [])

        if not hits:
            params["q"] = "cinematic mood dark"
            fallback_resp = requests.get(PIXABAY_SEARCH_URL, params=params, timeout=15)
            hits = fallback_resp.json().get("hits", [])

        for hit in hits:
            if len(downloaded) >= limit:
                break

            hit_id = hit.get("id")
            videos = hit.get("videos", {})
            chosen_stream = videos.get("large") or videos.get("medium") or videos.get("small")
            if not chosen_stream or not chosen_stream.get("url"):
                continue

            download_url = chosen_stream["url"]
            file_name = f"pixabay_{hit_id}_{_sanitize_filename(query)[:20]}.mp4"
            dest_path = output_dir / file_name

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                downloaded.append(dest_path)
                continue

            logger.info(f"Downloading B-roll '{query}' from Pixabay (ID: {hit_id})...")
            with requests.get(download_url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                downloaded.append(dest_path)

        return downloaded
    except Exception as e:
        logger.error(f"Error fetching from Pixabay: {e}")
        return downloaded


def fetch_from_pexels(
    api_key: str,
    query: str,
    output_dir: Path,
    limit: int = 1
) -> List[Path]:
    """
    Searches Pexels API for vertical video clips.
    """
    if not api_key:
        return []

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

    downloaded = []
    try:
        response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        videos = response.json().get("videos", [])

        if not videos:
            params["query"] = "dark cinematic mood"
            fallback_resp = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params, timeout=15)
            videos = fallback_resp.json().get("videos", [])

        for video in videos:
            if len(downloaded) >= limit:
                break

            video_id = video.get("id")
            video_files = video.get("video_files", [])
            chosen_file = None

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

            dest_path = output_dir / f"pexels_{video_id}_{_sanitize_filename(query)[:20]}.mp4"
            if dest_path.exists() and dest_path.stat().st_size > 50000:
                downloaded.append(dest_path)
                continue

            logger.info(f"Downloading B-roll '{query}' from Pexels (ID: {video_id})...")
            with requests.get(chosen_file["link"], stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=64 * 1024):
                        if chunk:
                            f.write(chunk)

            if dest_path.exists() and dest_path.stat().st_size > 50000:
                downloaded.append(dest_path)

        return downloaded
    except Exception as e:
        logger.error(f"Error fetching from Pexels: {e}")
        return downloaded


def fetch_all_broll_clips(
    pexels_key: str,
    pixabay_key: str,
    keywords_list: List[str],
    output_dir: Path,
    target_min_clips: int = 14
) -> List[Path]:
    """
    Downloads ample unique B-roll clips across keywords to avoid repetitive visual loops.
    Aims for at least target_min_clips (14+ unique clips).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    clips: List[Path] = []
    seen_ids = set()

    for kw in keywords_list:
        if pixabay_key:
            new_clips = fetch_from_pixabay(pixabay_key, kw, output_dir, limit=2)
            for c in new_clips:
                if c.name not in seen_ids:
                    seen_ids.add(c.name)
                    clips.append(c)

        if len(clips) < target_min_clips and pexels_key:
            new_clips = fetch_from_pexels(pexels_key, kw, output_dir, limit=1)
            for c in new_clips:
                if c.name not in seen_ids:
                    seen_ids.add(c.name)
                    clips.append(c)

        if len(clips) >= target_min_clips:
            break

    # If still below target, fetch supplementary atmospheric clips
    if len(clips) < 10 and pixabay_key:
        extra_queries = ["dramatic lighting portrait", "ancient architecture mystery", "storm clouds time lapse", "city night rain neon"]
        for eq in extra_queries:
            if len(clips) >= target_min_clips:
                break
            new_clips = fetch_from_pixabay(pixabay_key, eq, output_dir, limit=2)
            for c in new_clips:
                if c.name not in seen_ids:
                    seen_ids.add(c.name)
                    clips.append(c)

    return clips
