import asyncio
import base64
import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Tuple, Optional, List, Dict
import requests
import edge_tts

logger = logging.getLogger(__name__)

# Default top-quality high-retention English voices for Edge-TTS fallback
POPULAR_VOICES = {
    "christopher": "en-US-ChristopherNeural",  # Male, deep narrative, stoic / authoritative
    "guy": "en-US-GuyNeural",                  # Male, engaging, natural storytelling
    "jenny": "en-US-JennyNeural",              # Female, clear, modern, educational
    "ryan": "en-GB-RyanNeural",                # British Male, sophisticated documentary tone
    "sonia": "en-GB-SoniaNeural",              # British Female, crisp, articulate
}


def _format_srt_timestamp(seconds: float) -> str:
    """Converts seconds to SRT timestamp format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _get_audio_duration_seconds(audio_path: Path) -> float:
    """Gets audio duration using ffprobe."""
    try:
        from modules.video_engine import get_media_duration
        return get_media_duration(audio_path)
    except Exception:
        return 50.0


def _generate_proportional_srt(text: str, duration: float, srt_path: Path):
    """
    Generates word-chunked SRT subtitles proportional to the audio duration,
    accounting for sentence and clause pauses.
    """
    words = text.strip().split()
    if not words:
        return

    # Group into 3 words per line
    chunk_size = 3
    chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]
    
    # Calculate duration weights (longer chunks or chunks with punctuation get slightly more time)
    weights = []
    for c in chunks:
        weight = len(c.split())
        if c.endswith(('.', '!', '?')):
            weight += 1.2
        elif c.endswith((',', ';', ':')):
            weight += 0.5
        weights.append(weight)

    total_weight = sum(weights)
    srt_lines = []
    current_time = 0.2  # initial breathing room

    for i, (chunk, weight) in enumerate(zip(chunks, weights), 1):
        chunk_duration = (weight / total_weight) * (duration - 0.5)
        start_ts = _format_srt_timestamp(current_time)
        end_ts = _format_srt_timestamp(current_time + chunk_duration)
        srt_lines.append(f"{i}\n{start_ts} --> {end_ts}\n{chunk}\n")
        current_time += chunk_duration

    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text("\n".join(srt_lines), encoding="utf-8")


def _synthesize_fish_audio_voice(
    text: str,
    output_audio_path: Path,
    output_srt_path: Optional[Path],
    api_key: str,
    voice_id: str
) -> Tuple[Path, Optional[Path]]:
    """
    Synthesizes speech using Fish Audio Custom Voice Clone (Free Tier s2.1-pro-free).
    """
    url = "https://api.fish.audio/v1/tts"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "model": "s2.1-pro-free"
    }
    payload = {
        "text": text,
        "reference_id": voice_id,
        "format": "mp3"
    }

    logger.info(f"Synthesizing voice with Fish Audio Cloned Voice (Voice ID: {voice_id[:8]}...)...")
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    output_audio_path.write_bytes(response.content)
    logger.info(f"Generated cloned voice audio with Fish Audio: {output_audio_path}")

    # Generate synchronized kinetic subtitles
    if output_srt_path:
        duration = _get_audio_duration_seconds(output_audio_path)
        _generate_proportional_srt(text, duration, output_srt_path)
        logger.info(f"Generated synchronized subtitles at: {output_srt_path}")

    return output_audio_path, output_srt_path


def _synthesize_elevenlabs_voice(
    text: str,
    output_audio_path: Path,
    output_srt_path: Optional[Path],
    api_key: str,
    voice_id: str
) -> Tuple[Path, Optional[Path]]:
    """
    Synthesizes speech using ElevenLabs Voice Cloning API with word-level timestamps.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.2,
            "use_speaker_boost": True
        }
    }

    logger.info(f"Synthesizing voice with ElevenLabs Cloned Voice (ID: {voice_id[:8]}...)...")
    response = requests.post(url, headers=headers, json=payload, timeout=45)
    response.raise_for_status()

    data = response.json()
    audio_base64 = data.get("audio_base64")
    alignment = data.get("alignment", {})

    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_audio_path, "wb") as f:
        f.write(base64.b64decode(audio_base64))

    # Generate SRT from ElevenLabs alignment
    if output_srt_path and alignment:
        chars = alignment.get("characters", [])
        start_times = alignment.get("character_start_times_seconds", [])
        end_times = alignment.get("character_end_times_seconds", [])

        words_data: List[Dict] = []
        current_word = ""
        word_start = 0.0

        for i, char in enumerate(chars):
            if not current_word:
                word_start = start_times[i] if i < len(start_times) else 0.0

            if char == " " or i == len(chars) - 1:
                if char != " ":
                    current_word += char
                word_end = end_times[i] if i < len(end_times) else word_start + 0.3
                if current_word.strip():
                    words_data.append({
                        "word": current_word.strip(),
                        "start": word_start,
                        "end": word_end
                    })
                current_word = ""
            else:
                current_word += char

        srt_lines = []
        chunk_size = 3
        idx = 1
        for i in range(0, len(words_data), chunk_size):
            chunk = words_data[i : i + chunk_size]
            c_start = chunk[0]["start"]
            c_end = chunk[-1]["end"]
            c_text = " ".join([w["word"] for w in chunk])
            srt_lines.append(f"{idx}\n{_format_srt_timestamp(c_start)} --> {_format_srt_timestamp(c_end)}\n{c_text}\n")
            idx += 1

        output_srt_path.parent.mkdir(parents=True, exist_ok=True)
        output_srt_path.write_text("\n".join(srt_lines), encoding="utf-8")
        logger.info(f"Generated subtitles from ElevenLabs timestamps: {output_srt_path}")

    return output_audio_path, output_srt_path


async def _generate_edge_tts_async(
    text: str,
    output_audio_path: Path,
    output_srt_path: Optional[Path],
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> Tuple[Path, Optional[Path]]:
    """
    Asynchronously streams neural audio from Microsoft Edge-TTS and collects word boundaries.
    """
    output_audio_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
    sub_maker = edge_tts.SubMaker()

    with open(output_audio_path, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub_maker.feed(chunk)

    if output_srt_path:
        output_srt_path.parent.mkdir(parents=True, exist_ok=True)
        srt_content = sub_maker.get_srt()
        with open(output_srt_path, "w", encoding="utf-8") as srt_file:
            srt_file.write(srt_content)
        logger.info(f"Generated subtitles at: {output_srt_path}")

    logger.info(f"Generated neural audio at: {output_audio_path}")
    return output_audio_path, output_srt_path


def synthesize_voice(
    text: str,
    output_audio_path: Path,
    output_srt_path: Optional[Path] = None,
    voice: str = "en-US-ChristopherNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz",
    fish_audio_api_key: Optional[str] = None,
    fish_audio_voice_id: Optional[str] = None,
    elevenlabs_api_key: Optional[str] = None,
    elevenlabs_voice_id: Optional[str] = None
) -> Tuple[Path, Optional[Path]]:
    """
    Synthesizes speech using:
    1. Your Free Custom Voice Clone (Fish Audio) if keys are provided.
    2. ElevenLabs Voice Clone if configured.
    3. Microsoft Edge-TTS Neural Voice (100% Free) as default / fallback.
    """
    # Priority 1: Fish Audio Custom Voice Clone (100% Free!)
    if fish_audio_api_key and fish_audio_voice_id:
        try:
            return _synthesize_fish_audio_voice(
                text=text,
                output_audio_path=output_audio_path,
                output_srt_path=output_srt_path,
                api_key=fish_audio_api_key,
                voice_id=fish_audio_voice_id
            )
        except Exception as e:
            logger.warning(f"Fish Audio voice cloning synthesis failed: {e}. Trying fallback...")

    # Priority 2: ElevenLabs Voice Clone
    if elevenlabs_api_key and elevenlabs_voice_id:
        try:
            return _synthesize_elevenlabs_voice(
                text=text,
                output_audio_path=output_audio_path,
                output_srt_path=output_srt_path,
                api_key=elevenlabs_api_key,
                voice_id=elevenlabs_voice_id
            )
        except Exception as e:
            logger.warning(f"ElevenLabs voice cloning failed: {e}. Falling back to Edge-TTS...")

    # Priority 3: Free Microsoft Edge-TTS Neural Voice
    return asyncio.run(
        _generate_edge_tts_async(
            text=text,
            output_audio_path=output_audio_path,
            output_srt_path=output_srt_path,
            voice=voice,
            rate=rate,
            pitch=pitch
        )
    )
