import argparse
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"

def get_font(size: int, bold: bool = True):
    font_candidates = [
        # Linux standard paths
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Windows standard paths
        f"C:/Windows/Fonts/{'arialbd.ttf' if bold else 'arial.ttf'}",
        f"C:/Windows/Fonts/{'comicbd.ttf' if bold else 'comic.ttf'}",
        f"C:/Windows/Fonts/{'calibrib.ttf' if bold else 'calibri.ttf'}",
        f"C:/Windows/Fonts/{'segoeuib.ttf' if bold else 'segoeui.ttf'}",
        # Fallback names
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf"
    ]
    for fn in font_candidates:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def get_audio_duration(file_path: Path) -> float:
    cmd = [
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(res.stdout.strip())
    except Exception:
        return 3.0

def synthesize_outro_audio(text: str, out_path: Path):
    if out_path.exists() and out_path.stat().st_size > 1000:
        return
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Try importing voice engine from generate_essay
    try:
        from essay_stuff.generate_essay import synthesize_scene_voice
        success = synthesize_scene_voice(text, out_path)
        if success and out_path.exists() and out_path.stat().st_size > 1000:
            return
    except Exception:
        pass

    # Fallback to Edge-TTS Jenny or tone
    try:
        import asyncio
        import edge_tts
        async def _speak():
            comm = edge_tts.Communicate(text, "en-US-JennyNeural", rate="-2%")
            await comm.save(str(out_path))
        asyncio.run(_speak())
    except Exception as e:
        print(f"  [Shorts Outro] Edge-TTS note: {e}. Generating atmospheric tone fallback...")
        subprocess.run([
            FFMPEG, "-y",
            "-f", "lavfi", "-i", "sine=frequency=440:duration=0.5",
            "-af", "apad=whole_dur=3.5",
            str(out_path)
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def render_short_scene_frame(
    scene: Dict[str, Any],
    source_frame_path: Optional[Path],
    hook_title: str,
    out_path: Path
):
    w, h = 1080, 1920
    bg = Image.new("RGB", (w, h), (250, 250, 248))
    draw = ImageDraw.Draw(bg)

    f_badge = get_font(30, bold=True)
    f_hook = get_font(50, bold=True)
    f_caption = get_font(42, bold=True)
    f_cta = get_font(34, bold=True)

    # 1. Top Channel Badge
    draw.rounded_rectangle([340, 85, 740, 138], radius=25, fill=(20, 20, 20))
    draw.text((375, 96), "STATESIDE DOCS", fill=(255, 255, 255), font=f_badge)

    # 2. Top Topic Hook Title
    title_text = hook_title.upper()
    if len(title_text) > 28:
        title_text = title_text[:28] + "..."
    bbox = draw.textbbox((0, 0), title_text, font=f_hook)
    title_w = bbox[2] - bbox[0]
    draw.text(((w - title_w) // 2, 175), title_text, fill=(220, 30, 30), font=f_hook)
    draw.line([(80, 255), (1000, 255)], fill=(215, 215, 215), width=3)

    # 3. Illustration Viewport (Crop out horizontal banner to showcase the hand-drawn artwork)
    draw.rounded_rectangle([55, 280, 1025, 1020], radius=20, outline=(190, 190, 190), width=4, fill=(255, 255, 255))
    if source_frame_path and source_frame_path.exists():
        try:
            im_frame = Image.open(source_frame_path)
            # Crop center (x: 200..1720, y: 230..980)
            cropped = im_frame.crop((200, 310, 1720, 950))
            resized = cropped.resize((960, 720), Image.Resampling.LANCZOS)
            bg.paste(resized, (60, 290))
        except Exception as e:
            print(f"  [Frame Paste Warning] {e}")

    # 4. Kinetic Captions Zone
    draw.rounded_rectangle([70, 1060, 1010, 1480], radius=20, fill=(244, 244, 242), outline=(215, 215, 210), width=2)
    
    narration = scene.get("narration", "").strip()
    wrapped_lines = textwrap.wrap(narration, width=32)
    if not wrapped_lines:
        wrapped_lines = [scene.get("banner_text", "A TRUE CASE STUDY")]

    start_y = 1090 + max(0, (350 - len(wrapped_lines) * 58) // 2)
    highlight_keywords = [
        "29", "pills", "antidepressant", "overdose", "empty", "sugar",
        "heart", "148 bpm", "danger", "crashed", "paramedics", "shutting down",
        "nothing", "twin", "blood pressure", "doctor", "er bay", "cold sweat"
    ]

    for line in wrapped_lines[:6]:
        has_highlight = any(k in line.lower() for k in highlight_keywords)
        line_color = (220, 30, 30) if has_highlight and any(w in line.lower() for w in ["empty", "shutting down", "danger", "crashed"]) else (25, 25, 25)
        
        l_bbox = draw.textbbox((0, 0), line, font=f_caption)
        l_w = l_bbox[2] - l_bbox[0]
        draw.text(((w - l_w) // 2, start_y), line, fill=line_color, font=f_caption)
        start_y += 58

    # 5. Bottom Callout Button
    draw.rounded_rectangle([80, 1560, 1000, 1650], radius=45, fill=(220, 30, 30))
    cta_text = "► FULL 8-MIN DOCUMENTARY PINNED BELOW"
    c_bbox = draw.textbbox((0, 0), cta_text, font=f_cta)
    c_w = c_bbox[2] - c_bbox[0]
    draw.text(((w - c_w) // 2, 1584), cta_text, fill=(255, 255, 255), font=f_cta)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_path)

def render_short_outro_frame(
    hook_title: str,
    long_title: str,
    out_path: Path
):
    w, h = 1080, 1920
    bg = Image.new("RGB", (w, h), (250, 250, 248))
    draw = ImageDraw.Draw(bg)

    f_badge = get_font(30, bold=True)
    f_header = get_font(56, bold=True)
    f_sub = get_font(40, bold=False)
    f_cta = get_font(36, bold=True)

    # 1. Top Channel Badge
    draw.rounded_rectangle([340, 85, 740, 138], radius=25, fill=(20, 20, 20))
    draw.text((375, 96), "STATESIDE DOCS", fill=(255, 255, 255), font=f_badge)

    # 2. Main Outro Card
    draw.rounded_rectangle([70, 280, 1010, 1380], radius=25, fill=(255, 255, 255), outline=(200, 200, 200), width=4)

    draw.text((120, 350), "THE FULL STORY IS WAITING", fill=(220, 30, 30), font=f_header)
    draw.line([(120, 430), (960, 430)], fill=(220, 220, 220), width=3)

    # Hand-drawn icon / visual teaser inside outro
    draw.rounded_rectangle([150, 480, 930, 880], radius=20, fill=(245, 245, 243), outline=(210, 210, 210), width=2)
    draw.text((200, 560), "8-MINUTE INVESTIGATION", fill=(80, 80, 80), font=f_sub)
    draw.text((200, 630), "• Full Clinical Case Study", fill=(40, 40, 40), font=f_sub)
    draw.text((200, 700), "• The Biological Mechanism", fill=(40, 40, 40), font=f_sub)
    draw.text((200, 770), "• What This Means For You", fill=(40, 40, 40), font=f_sub)

    # Long video title
    wrapped_title = textwrap.wrap(long_title, width=28)
    cur_y = 940
    for line in wrapped_title[:3]:
        draw.text((140, cur_y), line, fill=(20, 20, 20), font=get_font(44, bold=True))
        cur_y += 56

    # 3. Big CTA Button
    draw.rounded_rectangle([120, 1160, 960, 1280], radius=60, fill=(220, 30, 30))
    cta_text = "► WATCH THE FULL DOCUMENTARY"
    c_bbox = draw.textbbox((0, 0), cta_text, font=f_cta)
    draw.text(((w - (c_bbox[2] - c_bbox[0])) // 2, 1200), cta_text, fill=(255, 255, 255), font=f_cta)

    # 4. Sticky Bottom Arrow
    sub_text = "Link is pinned at the top of comments"
    s_bbox = draw.textbbox((0, 0), sub_text, font=f_sub)
    draw.text(((w - (s_bbox[2] - s_bbox[0])) // 2, 1550), sub_text, fill=(60, 60, 60), font=f_sub)
    
    draw.rounded_rectangle([80, 1630, 1000, 1720], radius=45, fill=(20, 20, 20))
    cta_sub = "SUBSCRIBE FOR WEEKLY ESSAYS"
    cs_bbox = draw.textbbox((0, 0), cta_sub, font=f_cta)
    draw.text(((w - (cs_bbox[2] - cs_bbox[0])) // 2, 1656), cta_sub, fill=(255, 255, 255), font=f_cta)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out_path)


def generate_and_publish_short(
    work_dir: Path,
    script_data: Optional[Dict[str, Any]] = None,
    long_video_url: Optional[str] = None,
    upload: bool = True,
    max_duration: float = 54.0
) -> Dict[str, Any]:
    """
    Takes an existing long-form documentary directory, extracts the cold hook (Scenes 1..N),
    renders high-retention 9:16 vertical video essay frames, mixes audio, and uploads to YouTube Shorts
    with a pinned/top comment pointing to the full documentary.
    """
    work_dir = Path(work_dir)
    print("\n" + "=" * 65)
    print("🎬 STARTING STATESIDE SHORTS AUTO-CLIPPER ENGINE")
    print(f"👉 Target Work Dir: {work_dir}")
    print("=" * 65)

    # 1. Load Script Data
    if not script_data:
        script_files = list(work_dir.glob("script_*.json"))
        if script_files:
            with open(script_files[0], "r", encoding="utf-8") as f:
                script_data = json.load(f)
        else:
            raise FileNotFoundError(f"No script_*.json found in {work_dir}")

    # 2. Load YouTube Metadata if available
    yt_meta_file = work_dir / "youtube_metadata.json"
    if not long_video_url and yt_meta_file.exists():
        try:
            with open(yt_meta_file, "r", encoding="utf-8") as f:
                saved_meta = json.load(f)
                long_video_url = saved_meta.get("url") or saved_meta.get("long_video_url")
        except Exception:
            pass

    if not long_video_url:
        long_video_url = "https://www.youtube.com/@50kstateside"

    scenes = script_data.get("scenes", [])
    if not scenes:
        raise ValueError("Script contains no scenes.")

    hook_title = script_data.get("thumbnail_hook") or script_data.get("topic") or "THE MYSTERY"
    long_title = script_data.get("title") or "Stateside Documentary"

    audio_dir = work_dir / "audio"
    frames_dir = work_dir / "frames"
    
    shorts_dir = work_dir / "shorts_output"
    shorts_dir.mkdir(parents=True, exist_ok=True)
    short_frames_dir = shorts_dir / "frames"
    short_frames_dir.mkdir(parents=True, exist_ok=True)
    short_clips_dir = shorts_dir / "clips"
    short_clips_dir.mkdir(parents=True, exist_ok=True)

    # 3. Select Hook Scenes (Accumulate scenes up to max_duration - 4.0s for outro)
    target_hook_seconds = max_duration - 4.0
    selected_scenes = []
    cumulative_duration = 0.0

    for idx, scene in enumerate(scenes):
        sid = scene.get("scene_id", idx + 1)
        aud_file = audio_dir / f"scene_{sid:03d}.mp3"
        dur = get_audio_duration(aud_file) if aud_file.exists() else 3.5

        if cumulative_duration + dur > target_hook_seconds and len(selected_scenes) >= 4:
            break
        
        selected_scenes.append((scene, aud_file, dur))
        cumulative_duration += dur

    print(f"[Shorts Clipper] Selected first {len(selected_scenes)} hook scenes (Duration: {cumulative_duration:.1f}s)")

    # 4. Render Vertical 9:16 Frames and Compile Video Clips
    clip_files = []
    for idx, (scene, aud_file, dur) in enumerate(selected_scenes):
        sid = scene.get("scene_id", idx + 1)
        source_frame = frames_dir / f"scene_{sid:03d}.png"
        short_frame = short_frames_dir / f"short_frame_{sid:03d}.png"
        
        render_short_scene_frame(
            scene=scene,
            source_frame_path=source_frame,
            hook_title=hook_title,
            out_path=short_frame
        )

        clip_file = short_clips_dir / f"short_clip_{sid:03d}.mp4"
        if not (clip_file.exists() and clip_file.stat().st_size > 1000):
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", str(short_frame),
                "-i", str(aud_file),
                "-vf", "scale=1080:1920,format=yuv420p",
                "-c:v", "libx264",
                "-tune", "stillimage",
                "-preset", "veryfast",
                "-crf", "18",
                "-c:a", "aac",
                "-b:a", "192k",
                "-t", str(dur),
                "-shortest",
                str(clip_file)
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clip_files.append(clip_file)

    # 5. Render Outro Scene (Call-to-Action)
    outro_aud = shorts_dir / "outro.mp3"
    outro_text = f"Watch the complete 8-minute documentary on Stateside Docs. The link is pinned in the comments."
    synthesize_outro_audio(outro_text, outro_aud)
    outro_dur = get_audio_duration(outro_aud)

    outro_frame = short_frames_dir / "short_outro.png"
    render_short_outro_frame(
        hook_title=hook_title,
        long_title=long_title,
        out_path=outro_frame
    )

    outro_clip = short_clips_dir / "short_outro.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-loop", "1",
        "-i", str(outro_frame),
        "-i", str(outro_aud),
        "-vf", "scale=1080:1920,format=yuv420p",
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-preset", "veryfast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(outro_dur),
        "-shortest",
        str(outro_clip)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    clip_files.append(outro_clip)

    # 6. Concatenate All Clips
    concat_list = shorts_dir / "concat_short_clips.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in clip_files:
            posix_path = c.resolve().as_posix()
            f.write(f"file '{posix_path}'\n")

    master_short = shorts_dir / f"{work_dir.name}_short_master.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(master_short)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    total_short_dur = cumulative_duration + outro_dur
    print("\n" + "=" * 65)
    print("🏆 SHORTS MASTER READY!")
    print(f"👉 File: {master_short}")
    print(f"👉 Runtime: {total_short_dur:.1f}s (Strictly under 60s)")
    print("=" * 65 + "\n")

    # 7. Upload to YouTube Shorts & Post Top-Level Pinned Comment
    short_upload_res = None
    if upload:
        client_secrets = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")
        token_file = os.getenv("YOUTUBE_TOKEN_FILE", "oauth_token.json")
        
        if Path(token_file).exists() or Path(client_secrets).exists():
            from modules.youtube_uploader import upload_video_essay_to_youtube, post_video_comment
            
            short_title = f"{hook_title}: A Biological Paradox #Shorts"[:100]
            short_desc = f"""Watch the full documentary here: {long_video_url}

A man swallowed 29 antidepressant pills. His organs began shutting down, but every capsule was empty sugar. The biology of expectation.

Full documentary on Stateside Docs (@50kstateside).

#Shorts #psychology #documentary #science #humanbehavior #stateside
"""
            short_tags = ["Shorts", "psychology", "documentary", "science", "human behavior", "stateside", "50kstateside"]
            
            try:
                short_upload_res = upload_video_essay_to_youtube(
                    video_path=master_short,
                    title=short_title,
                    description=short_desc,
                    tags=short_tags,
                    client_secrets_file=client_secrets,
                    token_file=token_file,
                    thumbnail_path=None, # YouTube automatically assigns optimal vertical frame
                    privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
                    category_id="28"
                )
                
                short_vid_id = short_upload_res.get("id")
                if short_vid_id:
                    comment_text = f"👉 Watch the full 8-minute documentary breaking down the clinical papers here: {long_video_url}"
                    post_video_comment(
                        video_id=short_vid_id,
                        comment_text=comment_text,
                        client_secrets_file=client_secrets,
                        token_file=token_file
                    )
            except Exception as e:
                print(f"[Shorts Upload Warning] Could not complete upload: {e}")
        else:
            print("[Shorts Upload] Credentials file not found. Skipping auto-upload.")

    result = {
        "short_video_path": str(master_short.resolve()),
        "total_runtime_seconds": round(total_short_dur, 2),
        "long_video_url": long_video_url,
        "upload_result": short_upload_res
    }

    with open(shorts_dir / "short_metadata.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stateside Docs Shorts Auto-Clipper")
    parser.add_argument("--work-dir", type=str, required=True, help="Path to production essay folder")
    parser.add_argument("--long-url", type=str, default="", help="URL of published long-form documentary")
    parser.add_argument("--upload", action="store_true", help="Upload Short to YouTube and post funnel comment")
    args = parser.parse_args()

    generate_and_publish_short(
        work_dir=Path(args.work_dir),
        long_video_url=args.long_url if args.long_url else None,
        upload=args.upload
    )
