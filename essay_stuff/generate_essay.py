import os
import sys
import json
import re
import math
import asyncio
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import requests
from dotenv import load_dotenv

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

load_dotenv()

from config import settings
from essay_stuff.script_masterpiece_engine import (
    generate_masterpiece_script,
    CURATED_TOPIC_BANK,
    get_or_discover_next_topic,
    log_topic_produced
)
from essay_stuff.visual_masterpiece_engine import render_masterpiece_frame
from essay_stuff.thumbnail_engine import generate_zenn_style_thumbnail

def _resolve_binary(name: str, fallback_windows: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    if Path(fallback_windows).exists():
        return fallback_windows
    return name

FFMPEG = _resolve_binary(
    "ffmpeg",
    "C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
)
FFPROBE = _resolve_binary(
    "ffprobe",
    "C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffprobe.exe"
)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", getattr(settings, "ELEVENLABS_API_KEY", ""))
LOCKED_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" # George (ElevenLabs premade narrator)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:40]

async def _synthesize_edge_tts(text: str, out_path: Path):
    import edge_tts
    # en-US-ChristopherNeural has a deep, warm documentary resonance
    communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural", rate="-3%")
    await communicate.save(str(out_path))

def synthesize_scene_voice(text: str, out_path: Path, use_elevenlabs: bool = True) -> bool:
    """
    Synthesizes speech using ElevenLabs George, falling back seamlessly to Edge-TTS.
    """
    if out_path.exists() and out_path.stat().st_size > 500:
        return True # Cached
        
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    if use_elevenlabs and ELEVENLABS_API_KEY:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{LOCKED_VOICE_ID}"
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.55,
                "similarity_boost": 0.85,
                "style": 0.15,
                "use_speaker_boost": True
            }
        }
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=25)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
            else:
                print(f"    [ElevenLabs Warning] HTTP {r.status_code}: {r.text[:120]}. Falling back to Edge-TTS.")
        except Exception as e:
            print(f"    [ElevenLabs Warning] Exception: {e}. Falling back to Edge-TTS.")
            
    # Fallback to high-quality Edge-TTS
    try:
        asyncio.run(_synthesize_edge_tts(text, out_path))
        return True
    except Exception as e:
        print(f"    [Edge-TTS Error] Failed: {e}")
        return False

def get_audio_duration(audio_path: Path) -> float:
    cmd = [
        FFPROBE, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return float(res.stdout.strip())

def format_timestamp(seconds: float) -> str:
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def generate_full_video_essay(
    topic: str,
    target_scenes: int = 55,
    skip_script: bool = False,
    allow_elevenlabs: bool = True,
    upload: bool = False
) -> Path:
    slug = slugify(topic)
    work_dir = Path("output") / "essays" / slug
    work_dir.mkdir(parents=True, exist_ok=True)
    
    script_path = work_dir / f"script_{slug}.json"
    
    # -------------------------------------------------------------------------
    # Step 1: Script Engine
    # -------------------------------------------------------------------------
    print("\n" + "=" * 65)
    print(f"🎬 MASTERPIECE DOCUMENTARY ENGINE: {topic.upper()}")
    print("=" * 65)
    
    if skip_script and script_path.exists():
        print(f"[Step 1/5] Loading existing script from: {script_path}")
        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)
    else:
        print(f"[Step 1/5] Generating 5-Movement Masterpiece Script with Gemini...")
        script_data = generate_masterpiece_script(topic, target_scenes=target_scenes)
        with open(script_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        print(f"  -> Title: {script_data.get('title')}")
        print(f"  -> Scenes: {len(script_data.get('scenes', []))}")
        print(f"  -> Saved script to {script_path}")
        
    scenes = script_data.get("scenes", [])
    if not scenes:
        raise ValueError("Script contains no scenes.")
        
    audio_dir = work_dir / "audio"
    frames_dir = work_dir / "frames"
    clips_dir = work_dir / "clips"
    audio_dir.mkdir(exist_ok=True)
    frames_dir.mkdir(exist_ok=True)
    clips_dir.mkdir(exist_ok=True)
    
    # -------------------------------------------------------------------------
    # Step 2: Voiceover Synthesis (ElevenLabs George / Edge-TTS Fallback)
    # -------------------------------------------------------------------------
    print(f"\n[Step 2/5] Synthesizing Voiceover for {len(scenes)} scenes...")
    scene_durations = []
    cumulative_time = 0.0
    timestamps_chapters = []
    
    for s in scenes:
        sid = s["scene_id"]
        narration = s["narration"]
        aud_file = audio_dir / f"scene_{sid:03d}.mp3"
        
        synthesize_scene_voice(narration, aud_file, use_elevenlabs=allow_elevenlabs)
        dur = get_audio_duration(aud_file)
        scene_durations.append(dur)
        
        # Track chapter markers every 10-12 scenes
        if sid == 1 or sid == 9 or sid == 18 or sid == 34 or sid == 48:
            timestamps_chapters.append((cumulative_time, s.get("banner_text", f"Part {sid}")))
            
        cumulative_time += dur
        if sid % 10 == 0 or sid == len(scenes):
            print(f"  -> Progress: Synthesized {sid}/{len(scenes)} scenes ({cumulative_time:.1f}s total)")
            
    # -------------------------------------------------------------------------
    # Step 3: Visual Masterpiece Frame Rendering (1080p Static Doodles)
    # -------------------------------------------------------------------------
    print(f"\n[Step 3/5] Rendering {len(scenes)} rock-solid 1080p hand-drawn doodle frames...")
    frame_files = []
    for s in scenes:
        sid = s["scene_id"]
        frame_file = frames_dir / f"scene_{sid:03d}.png"
        if not frame_file.exists():
            render_masterpiece_frame(s, frame_file)
        frame_files.append(frame_file)
        if sid % 15 == 0 or sid == len(scenes):
            print(f"  -> Progress: Rendered {sid}/{len(scenes)} frames...")
            
    # -------------------------------------------------------------------------
    # Step 4: Render Video Clips & Concatenate
    # -------------------------------------------------------------------------
    print(f"\n[Step 4/5] Compiling {len(scenes)} video clips with FFmpeg...")
    clip_files = []
    for idx, s in enumerate(scenes):
        sid = s["scene_id"]
        frame_file = frame_files[idx]
        aud_file = audio_dir / f"scene_{sid:03d}.mp3"
        clip_file = clips_dir / f"clip_{sid:03d}.mp4"
        dur = scene_durations[idx]
        
        if not (clip_file.exists() and clip_file.stat().st_size > 1000):
            cmd = [
                FFMPEG, "-y",
                "-loop", "1",
                "-i", str(frame_file),
                "-i", str(aud_file),
                "-vf", "scale=1920:1080,format=yuv420p",
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
        if sid % 15 == 0 or sid == len(scenes):
            print(f"  -> Progress: Compiled {sid}/{len(scenes)} clips...")
            
    # Concat demuxer
    concat_list = work_dir / "concat_clips.txt"
    with open(concat_list, "w", encoding="utf-8") as f:
        for c in clip_files:
            posix_path = c.resolve().as_posix()
            f.write(f"file '{posix_path}'\n")
            
    temp_concat = work_dir / "temp_concatenated.mp4"
    subprocess.run([
        FFMPEG, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(temp_concat)
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # -------------------------------------------------------------------------
    # Step 5: Sub-Bass Tension Drone Mixing & Anti-AI Metadata Spoofing
    # -------------------------------------------------------------------------
    print(f"\n[Step 5/5] Mixing 55Hz sub-bass atmospheric drone and anti-AI metadata...")
    master_video = work_dir / f"{slug}_master.mp4"
    channel_name = os.getenv("CHANNEL_NAME", "Stateside")
    channel_handle = os.getenv("CHANNEL_HANDLE", "@50kstateside")
    
    mix_cmd = [
        FFMPEG, "-y",
        "-i", str(temp_concat),
        "-f", "lavfi",
        "-i", "aevalsrc=exprs='0.02*sin(2*PI*55*t)+0.01*sin(2*PI*110*t)':s=44100",
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:weights=1.0 0.10[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map_metadata", "-1",
        "-metadata", f"title={script_data.get('title', topic)}",
        "-metadata", f"artist={channel_name}",
        "-metadata", f"comment=Mastered in DaVinci Resolve Studio 19.1 for {channel_name} ({channel_handle})",
        str(master_video)
    ]
    subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if temp_concat.exists():
        temp_concat.unlink()
        
    # -------------------------------------------------------------------------
    # Step 6: Generate YouTube Metadata Package & Cover Thumbnail
    # -------------------------------------------------------------------------
    # Look up enriched metadata from curated bank or script data
    curated_info = CURATED_TOPIC_BANK.get(topic.lower(), {})
    hook_lines_list = script_data.get("hook_summary_lines") or curated_info.get("hook_summary_lines") or [
        "A fascinating phenomenon unfolds when expectations collide with biology.",
        "The results are measurable down to the decimal point."
    ]
    hook_lines_text = "\n".join(hook_lines_list)
    case_summary = script_data.get("case_study_summary") or curated_info.get("case_study_summary") or ""
    concept_thesis = script_data.get("conceptual_thesis") or curated_info.get("conceptual_thesis") or ""
    empirical_tease = script_data.get("empirical_study_summary") or curated_info.get("empirical_study_summary") or ""
    
    what_covers_list = script_data.get("what_this_covers") or curated_info.get("what_this_covers") or [
        f"The physiological mechanism behind {topic}",
        "The clinical study that proved the paradox",
        "How words and expectations physically alter the body",
        "What this reveals about human social evolution"
    ]
    covers_text = "\n".join([f"- {item}" for item in what_covers_list])
    takeaway = script_data.get("philosophical_takeaway") or curated_info.get("philosophical_takeaway") or "Knowing that is where the choice starts."
    
    # Formatted sources with APA citations and plain English explanations
    sources_detailed = script_data.get("sources_detailed") or curated_info.get("sources_detailed") or []
    sources_blocks = []
    for s_entry in sources_detailed:
        heading = s_entry.get("heading", "").upper()
        citation = s_entry.get("citation", "")
        summary = s_entry.get("summary", "")
        sources_blocks.append(f"{heading}\n{citation}\n{summary}")
        
    if not sources_blocks and script_data.get("sources"):
        sources_blocks = ["\n".join([f"- {s}" for s in script_data.get("sources", [])])]
        
    formatted_sources = "\n\n".join(sources_blocks)
    
    yt_description = f"""#psychology #science #documentary
{hook_lines_text}

{case_summary}

{concept_thesis}

{empirical_tease}

What this covers:
{covers_text}

{takeaway}

____________________

💖 I make these alone, please like this video if you have the time. If not, no problem. I will see you in the next one.

- {channel_name}

____________________

S O U R C E S
____________________

{formatted_sources}

____________________

#psychology #science #documentary #{slug} #{channel_name.lower()}
"""

    # Generate High-CTR Thumbnail
    thumb_hook = script_data.get("thumbnail_hook") or curated_info.get("thumbnail_hook") or "WHY NOT?"
    thumbnail_path = work_dir / "thumbnail.png"
    generate_zenn_style_thumbnail(thumb_hook, topic, thumbnail_path)

    yt_metadata = {
        "title": script_data.get("title"),
        "channel": channel_name,
        "handle": channel_handle,
        "thumbnail_hook": thumb_hook,
        "thumbnail_path": str(thumbnail_path.resolve()),
        "description": yt_description.strip(),
        "tags": ["psychology", "documentary", "science", "human behavior", "storytelling", "facts", "stateside", "50kstateside"],
        "category_id": "28", # Science & Technology
        "total_runtime_seconds": round(cumulative_time, 2),
        "total_scenes": len(scenes),
        "master_video_path": str(master_video.resolve())
    }
    
    with open(work_dir / "youtube_metadata.json", "w", encoding="utf-8") as f:
        json.dump(yt_metadata, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 65)
    print("🏆 MASTERPIECE PRODUCTION COMPLETE!")
    print(f"👉 Master Video: {master_video}")
    print(f"👉 Thumbnail: {thumbnail_path}")
    print(f"👉 Runtime: {format_timestamp(cumulative_time)} ({cumulative_time:.1f}s)")
    print(f"👉 Metadata: {work_dir / 'youtube_metadata.json'}")
    print("=" * 65 + "\n")

    # -------------------------------------------------------------------------
    # Step 7: Optional YouTube Upload
    # -------------------------------------------------------------------------
    if upload:
        from modules.youtube_uploader import upload_video_essay_to_youtube
        client_secrets = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secret.json")
        token_file = os.getenv("YOUTUBE_TOKEN_FILE", "oauth_token.json")
        upload_video_essay_to_youtube(
            video_path=master_video,
            title=yt_metadata["title"],
            description=yt_metadata["description"],
            tags=yt_metadata["tags"],
            client_secrets_file=client_secrets,
            token_file=token_file,
            thumbnail_path=thumbnail_path,
            privacy_status=os.getenv("YOUTUBE_PRIVACY_STATUS", "public"),
            category_id="28"
        )
    
    # -------------------------------------------------------------------------
    # Step 8: Log topic to prevent duplicate posting
    # -------------------------------------------------------------------------
    log_topic_produced(topic)
    
    return master_video

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="End-to-End Video Essay Production")
    parser.add_argument("--topic", type=str, default="auto", help="Topic key, custom prompt, or 'auto'")
    parser.add_argument("--scenes", type=int, default=55, help="Target scene count")
    parser.add_argument("--skip-script", action="store_true", help="Use existing script file if available")
    parser.add_argument("--allow-elevenlabs", action="store_true", default=True, help="Use ElevenLabs voice")
    parser.add_argument("--upload", action="store_true", help="Automatically upload completed video to YouTube")
    args = parser.parse_args()
    
    selected_topic = args.topic
    if selected_topic == "auto" or not selected_topic:
        selected_topic = get_or_discover_next_topic()
        print(f"🤖 AUTOPILOT TOPIC SELECTED: {selected_topic}")
    
    generate_full_video_essay(
        topic=selected_topic,
        target_scenes=args.scenes,
        skip_script=args.skip_script,
        allow_elevenlabs=args.allow_elevenlabs,
        upload=args.upload
    )
