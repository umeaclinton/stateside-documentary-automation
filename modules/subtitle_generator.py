import logging
import re
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)


def _parse_srt_timestamp(ts_str: str) -> float:
    """Converts SRT timestamp '00:01:23,456' or '00:01:23.456' to seconds."""
    ts_str = ts_str.replace(',', '.')
    parts = ts_str.strip().split(':')
    if len(parts) == 3:
        return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return 0.0


def _format_ass_timestamp(seconds: float) -> str:
    """Converts seconds into ASS timestamp format 'H:MM:SS.cs' (centiseconds)."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def srt_to_kinetic_ass(
    srt_path: Path,
    ass_path: Path,
    font_name: str = "Arial",
    font_size: int = 68,
    primary_color: str = "&H00FFFFFF",
    outline_color: str = "&H00000000",
    highlight_color: str = "&H0000FFFF"
) -> Path:
    """
    Converts standard SRT subtitle cues into animated, high-retention
    Advanced SubStation Alpha (.ass) subtitles with bold outlines and kinetic chunking.
    """
    if not srt_path.exists():
        raise FileNotFoundError(f"SRT file not found: {srt_path}")

    raw_text = srt_path.read_text(encoding="utf-8")
    
    # Parse SRT blocks
    blocks = re.split(r'\n\s*\n', raw_text.strip())
    cues: List[Dict] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) >= 3:
            # line 0 is index, line 1 is timestamp, line 2+ is text
            time_match = re.match(r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})', lines[1])
            if time_match:
                start_sec = _parse_srt_timestamp(time_match.group(1))
                end_sec = _parse_srt_timestamp(time_match.group(2))
                cue_text = " ".join(lines[2:])
                cues.append({
                    "start": start_sec,
                    "end": end_sec,
                    "text": cue_text
                })

    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ShortsDefault,{font_name},{font_size},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,1,0,1,6,3,2,60,60,620,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    dialogue_lines: List[str] = []

    for cue in cues:
        start_ass = _format_ass_timestamp(cue["start"])
        end_ass = _format_ass_timestamp(cue["end"])
        words = cue["text"].upper().split()
        
        if not words:
            continue

        # Chunk into 3-4 words per line for rapid dynamic reading
        chunk_size = 3
        total_duration = max(0.1, cue["end"] - cue["start"])
        
        num_chunks = max(1, (len(words) + chunk_size - 1) // chunk_size)
        time_per_chunk = total_duration / num_chunks

        for i in range(num_chunks):
            sub_words = words[i * chunk_size : (i + 1) * chunk_size]
            c_start = cue["start"] + (i * time_per_chunk)
            c_end = min(cue["end"], c_start + time_per_chunk)

            # Highlight first word with yellow/gold accent color
            if len(sub_words) > 1:
                formatted_text = f"{{\\c{highlight_color}}}{sub_words[0]}{{\\c{primary_color}}} {' '.join(sub_words[1:])}"
            else:
                formatted_text = f"{{\\c{highlight_color}}}{sub_words[0]}"

            dialogue_lines.append(
                f"Dialogue: 0,{_format_ass_timestamp(c_start)},{_format_ass_timestamp(c_end)},ShortsDefault,,0,0,0,,{formatted_text}"
            )

    ass_path.parent.mkdir(parents=True, exist_ok=True)
    ass_path.write_text(ass_header + "\n".join(dialogue_lines) + "\n", encoding="utf-8")
    logger.info(f"Generated kinetic ASS subtitles: {ass_path}")
    return ass_path
