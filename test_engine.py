import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.voice_synthesizer import synthesize_voice
from modules.subtitle_generator import srt_to_kinetic_ass
from modules.video_engine import render_short_video, create_solid_color_background

def test_pipeline_engine():
    print("Testing Edge-TTS & Video Engine...")
    test_dir = Path("output/test_run")
    test_dir.mkdir(parents=True, exist_ok=True)

    text = "Most people react with anger when criticized. But Marcus Aurelius taught that silence is the ultimate weapon against disrespect."
    audio_path = test_dir / "test_audio.mp3"
    srt_path = test_dir / "test_subs.srt"
    ass_path = test_dir / "test_subs.ass"
    video_path = test_dir / "test_output.mp4"

    # Step 1: Synthesize voice
    print("1. Synthesizing voice...")
    synthesize_voice(text, audio_path, srt_path, voice="en-US-ChristopherNeural")
    assert audio_path.exists() and audio_path.stat().st_size > 0, "Audio failed"
    assert srt_path.exists() and srt_path.stat().st_size > 0, "SRT failed"
    print(f"Audio & SRT generated successfully! Size: {audio_path.stat().st_size} bytes")

    # Step 2: Convert to kinetic subtitles
    print("2. Converting to kinetic ASS subtitles...")
    srt_to_kinetic_ass(srt_path, ass_path)
    assert ass_path.exists() and ass_path.stat().st_size > 0, "ASS failed"
    print(f"ASS subtitles generated! Size: {ass_path.stat().st_size} bytes")

    # Step 3: Render sample video with solid background
    print("3. Rendering video composite with FFmpeg...")
    canvas = test_dir / "test_bg.mp4"
    create_solid_color_background(canvas, duration=15.0)
    render_short_video(
        audio_path=audio_path,
        broll_clips=[canvas],
        ass_subtitles_path=ass_path,
        output_video_path=video_path,
        clip_duration=4.0
    )
    assert video_path.exists() and video_path.stat().st_size > 0, "Video render failed"
    print(f"SUCCESS! Rendered test video at: {video_path} (Size: {video_path.stat().st_size} bytes)")

if __name__ == "__main__":
    test_pipeline_engine()
