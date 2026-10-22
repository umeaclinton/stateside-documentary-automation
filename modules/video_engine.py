import json
import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def get_ffmpeg_path() -> str:
    """Finds FFmpeg executable in system PATH, WinGet directories, or via imageio_ffmpeg."""
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    # Check WinGet installation locations on Windows
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pattern = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        for candidate in winget_pattern.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"):
            if candidate.exists():
                return str(candidate)

    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    raise RuntimeError("FFmpeg executable could not be found.")


def get_ffprobe_path() -> str:
    """Finds FFprobe executable in system PATH, WinGet directories, or derives it from FFmpeg."""
    system_ffprobe = shutil.which("ffprobe")
    if system_ffprobe:
        return system_ffprobe

    # Check WinGet installation locations on Windows
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pattern = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        for candidate in winget_pattern.glob("Gyan.FFmpeg*/**/bin/ffprobe.exe"):
            if candidate.exists():
                return str(candidate)

    ffmpeg_exe = get_ffmpeg_path()
    candidate = Path(ffmpeg_exe).parent / ("ffprobe.exe" if os.name == "nt" else "ffprobe")
    if candidate.exists():
        return str(candidate)
    return "ffprobe"


def get_media_duration(file_path: Path) -> float:
    """Returns the duration of an audio or video file in seconds."""
    ffprobe_cmd = [
        get_ffprobe_path(),
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    try:
        result = subprocess.run(ffprobe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.warning(f"Failed to probe duration with ffprobe for {file_path}: {e}")
        # Fallback estimation based on file size or default 50s
        return 50.0


def _escape_filter_path(file_path: Path) -> str:
    """Escapes file paths for FFmpeg complex filter graphs (especially on Windows)."""
    p_str = str(file_path.resolve()).replace("\\", "/")
    # Escape colon after drive letter: C:/ -> C\\:/
    if len(p_str) > 1 and p_str[1] == ":":
        p_str = p_str[0] + "\\:" + p_str[2:]
    return p_str


def create_solid_color_background(output_path: Path, duration: float = 50.0) -> Path:
    """Fallback generator for a dark gradient background if no B-roll is available."""
    ffmpeg = get_ffmpeg_path()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y",
        "-f", "lavfi",
        "-i", f"color=c=0x111116:s=1080x1920:d={duration}:r=30",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    return output_path


def render_short_video(
    audio_path: Path,
    broll_clips: List[Path],
    ass_subtitles_path: Optional[Path],
    output_video_path: Path,
    background_music_path: Optional[Path] = None,
    clip_duration: float = 4.0
) -> Path:
    """
    Assembles vertical 1080x1920 video:
    - Cycles & stitches B-roll clips every ~4 seconds with portrait crop.
    - Synchronizes with narration voiceover audio.
    - Ducked background music (optional).
    - Burns kinetic ASS subtitles into the video stream.
    """
    ffmpeg = get_ffmpeg_path()
    output_video_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_video_path.parent / "temp_render"
    temp_dir.mkdir(parents=True, exist_ok=True)

    total_duration = get_media_duration(audio_path)
    logger.info(f"Target video duration (from narration): {total_duration:.2f} seconds")

    # If no B-roll available, create a clean moody dark canvas
    if not broll_clips:
        logger.warning("No B-roll clips provided! Generating clean dark canvas background...")
        fallback_clip = temp_dir / "dark_canvas.mp4"
        create_solid_color_background(fallback_clip, duration=total_duration + 5)
        broll_clips = [fallback_clip]

    # Step 1: Pre-process each clip to standard 1080x1920 30fps without audio
    processed_clips = []
    for i, clip in enumerate(broll_clips):
        processed_clip = temp_dir / f"clip_proc_{i}.mp4"
        vf_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "fps=30"
        )
        cmd = [
            ffmpeg, "-y",
            "-ss", "0",
            "-t", str(clip_duration),
            "-i", str(clip),
            "-vf", vf_filter,
            "-an",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            str(processed_clip)
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            processed_clips.append(processed_clip)
        except subprocess.CalledProcessError as e:
            logger.warning(f"Could not process clip {clip}: {e.stderr.decode('utf-8', errors='ignore')}")

    if not processed_clips:
        fallback_clip = temp_dir / "fallback_canvas.mp4"
        create_solid_color_background(fallback_clip, duration=total_duration + 5)
        processed_clips = [fallback_clip]

    # Step 2: Build concat list file to loop clips until total duration is satisfied
    concat_list_file = temp_dir / "concat_list.txt"
    lines = []
    accumulated_dur = 0.0
    idx = 0
    while accumulated_dur < (total_duration + 5.0):
        clip = processed_clips[idx % len(processed_clips)]
        escaped_clip_path = str(clip.resolve()).replace("\\", "/")
        lines.append(f"file '{escaped_clip_path}'")
        accumulated_dur += clip_duration
        idx += 1

    concat_list_file.write_text("\n".join(lines), encoding="utf-8")

    # Step 3: Concatenate video stream
    concatenated_video = temp_dir / "stitched_broll.mp4"
    concat_cmd = [
        ffmpeg, "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(concatenated_video)
    ]
    subprocess.run(concat_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

    # Step 4: Final composite with audio and subtitles
    # Inputs:
    # 0: stitched video
    # 1: voice narration audio
    inputs = [
        "-i", str(concatenated_video),
        "-i", str(audio_path)
    ]

    filter_complex = []
    
    # Check if optional background music exists
    has_bg_music = background_music_path and background_music_path.exists()
    if has_bg_music:
        inputs.extend(["-stream_loop", "-1", "-i", str(background_music_path)])
        # Mix narration (100%) and bg_music (12%)
        filter_complex.append("[1:a]volume=1.0[voice];[2:a]volume=0.12[bg];[voice][bg]amix=inputs=2:duration=first[aout]")
        audio_map = "[aout]"
    else:
        audio_map = "1:a"

    # Subtitle burning
    if ass_subtitles_path and ass_subtitles_path.exists():
        escaped_ass = _escape_filter_path(ass_subtitles_path)
        video_filter = f"subtitles='{escaped_ass}'"
    else:
        video_filter = "null"

    render_cmd = [
        ffmpeg, "-y",
        *inputs,
        "-vf", video_filter,
    ]

    if filter_complex:
        render_cmd.extend(["-filter_complex", ";".join(filter_complex), "-map", "0:v", "-map", audio_map])
    else:
        render_cmd.extend(["-map", "0:v", "-map", "1:a"])

    render_cmd.extend([
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", f"{total_duration:.2f}",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_video_path)
    ])

    logger.info(f"Rendering final YouTube Short to: {output_video_path}...")
    run_res = subprocess.run(render_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if run_res.returncode != 0:
        err_msg = run_res.stderr.decode("utf-8", errors="ignore")
        logger.error(f"FFmpeg render error: {err_msg}")
        raise RuntimeError(f"FFmpeg render failed: {err_msg}")

    logger.info(f"Short successfully created at: {output_video_path} ({total_duration:.1f}s)")
    return output_video_path
