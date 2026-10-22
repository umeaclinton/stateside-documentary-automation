import argparse
import datetime
import json
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("YouTubeShortsPipeline")

from config import settings
from modules.script_generator import generate_short_script
from modules.voice_synthesizer import synthesize_voice
from modules.video_fetcher import fetch_all_broll_clips
from modules.subtitle_generator import srt_to_kinetic_ass
from modules.video_engine import render_short_video
from modules.youtube_uploader import upload_short_to_youtube


def run_pipeline(
    topic: str = None,
    niche: str = None,
    voice: str = None,
    skip_upload: bool = False,
    privacy_status: str = None
):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = settings.OUTPUT_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    niche = niche or settings.CONTENT_NICHE
    voice = voice or settings.VOICE_NAME
    privacy = privacy_status or settings.YOUTUBE_PRIVACY_STATUS

    print("=" * 65)
    print("🎬 STARTING ZERO-COST YOUTUBE SHORTS AUTOMATION PIPELINE")
    print(f"📌 Niche: {niche}")
    print(f"🎙️ Voice: {voice}")
    print(f"📁 Output Run Directory: {run_dir}")
    print("=" * 65)

    # -------------------------------------------------------------
    # Step 1: Generate Script via Gemini API
    # -------------------------------------------------------------
    logger.info(">>> STEP 1/5: Generating high-retention script with Gemini API...")
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is missing! Add GEMINI_API_KEY to your .env file or GitHub Secrets."
        )

    script_obj = generate_short_script(
        api_key=settings.GEMINI_API_KEY,
        niche=niche,
        specific_topic=topic
    )

    script_file = run_dir / "script.json"
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script_obj.model_dump(), f, indent=2, ensure_ascii=False)
    
    print(f"\n📖 Title: {script_obj.title}")
    print(f"🎯 Hook: {script_obj.hook}")
    print(f"📜 Scenes to render: {len(script_obj.scenes)}\n")

    # -------------------------------------------------------------
    # Step 2: Synthesize Voiceover & Timestamps via Edge-TTS (100% Free)
    # -------------------------------------------------------------
    logger.info(">>> STEP 2/5: Synthesizing neural voiceover via Microsoft Edge-TTS...")
    audio_path = run_dir / "voiceover.mp3"
    srt_path = run_dir / "subtitles.srt"

    synthesize_voice(
        text=script_obj.full_narration,
        output_audio_path=audio_path,
        output_srt_path=srt_path,
        voice=voice,
        rate=settings.VOICE_RATE,
        pitch=settings.VOICE_PITCH
    )

    # -------------------------------------------------------------
    # Step 3: Fetch Vertical B-Roll Footage via Pexels API
    # -------------------------------------------------------------
    logger.info(">>> STEP 3/5: Searching & fetching vertical B-roll clips from Pexels...")
    clips_dir = run_dir / "broll"
    
    # Collect all unique keywords from the generated scenes
    all_keywords = []
    for scene in script_obj.scenes:
        for kw in scene.broll_keywords:
            if kw not in all_keywords:
                all_keywords.append(kw)

    # Limit to top 5-7 keyword clips
    selected_keywords = all_keywords[:7] if all_keywords else ["stoic moody dark portrait", "mind focus contemplation"]
    logger.info(f"Visual keywords to fetch: {selected_keywords}")

    downloaded_clips = []
    if settings.PEXELS_API_KEY:
        downloaded_clips = fetch_all_broll_clips(
            api_key=settings.PEXELS_API_KEY,
            keywords_list=selected_keywords,
            output_dir=clips_dir
        )
    else:
        logger.warning("PEXELS_API_KEY not configured. Running with fallback canvas.")

    logger.info(f"Acquired {len(downloaded_clips)} B-roll clips.")

    # -------------------------------------------------------------
    # Step 4: Convert Subtitles to Kinetic ASS Format
    # -------------------------------------------------------------
    logger.info(">>> STEP 4/5: Generating kinetic animated captions...")
    ass_path = run_dir / "subtitles.ass"
    srt_to_kinetic_ass(
        srt_path=srt_path,
        ass_path=ass_path,
        font_name=settings.FONT_NAME,
        font_size=settings.FONT_SIZE,
        primary_color=settings.FONT_COLOR,
        outline_color=settings.OUTLINE_COLOR,
        highlight_color=settings.HIGHLIGHT_COLOR
    )

    # -------------------------------------------------------------
    # Step 5: Render Final 1080x1920 Short via FFmpeg
    # -------------------------------------------------------------
    logger.info(">>> STEP 5/5: Rendering final video composition via FFmpeg...")
    final_video_path = run_dir / "final_short.mp4"
    
    # Look for optional background music in assets/audio
    bg_music = None
    if settings.AUDIO_ASSETS_DIR.exists():
        audio_files = list(settings.AUDIO_ASSETS_DIR.glob("*.mp3")) + list(settings.AUDIO_ASSETS_DIR.glob("*.wav"))
        if audio_files:
            bg_music = audio_files[0]
            logger.info(f"Using background music track: {bg_music.name}")

    render_short_video(
        audio_path=audio_path,
        broll_clips=downloaded_clips,
        ass_subtitles_path=ass_path,
        output_video_path=final_video_path,
        background_music_path=bg_music,
        clip_duration=settings.MIN_CLIP_DURATION
    )

    print("\n" + "=" * 65)
    print(f"🎉 VIDEO CREATION COMPLETED SUCCESSFULLY!")
    print(f"📺 Video File: {final_video_path}")
    print("=" * 65 + "\n")

    # -------------------------------------------------------------
    # Step 6: Upload to YouTube (Optional / Scheduled)
    # -------------------------------------------------------------
    if skip_upload:
        logger.info("⏩ Skipping YouTube upload as requested (--skip-upload).")
        return final_video_path

    logger.info(">>> STEP 6/6: Uploading Short to YouTube...")
    try:
        upload_result = upload_short_to_youtube(
            video_path=final_video_path,
            title=script_obj.title,
            description=script_obj.description,
            tags=script_obj.tags,
            client_secrets_file=settings.YOUTUBE_CLIENT_SECRETS_FILE,
            token_file=settings.YOUTUBE_TOKEN_FILE,
            privacy_status=privacy
        )
        print(f"\n🚀 SHORT PUBLISHED! View it here: {upload_result['url']}\n")
    except Exception as e:
        logger.error(f"YouTube Upload Failed: {e}")
        print("\n⚠️ Note: The video was rendered successfully, but YouTube upload could not proceed.")
        print("To enable uploads, ensure client_secret.json and oauth_token.json are present.\n")

    return final_video_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Zero-Cost YouTube Shorts Generator & Poster")
    parser.add_argument("--topic", type=str, default=None, help="Specific topic or prompt for the video")
    parser.add_argument("--niche", type=str, default=None, help="Target niche (e.g. 'Stoicism', 'Psychology')")
    parser.add_argument("--voice", type=str, default=None, help="Microsoft Edge-TTS voice name")
    parser.add_argument("--skip-upload", action="store_true", help="Render video locally without uploading to YouTube")
    parser.add_argument("--privacy", type=str, default=None, choices=["public", "unlisted", "private"], help="YouTube privacy")

    args = parser.parse_args()

    run_pipeline(
        topic=args.topic,
        niche=args.niche,
        voice=args.voice,
        skip_upload=args.skip_upload,
        privacy_status=args.privacy
    )
