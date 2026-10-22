import asyncio
import logging
from pathlib import Path
from typing import Tuple, Optional
import edge_tts

logger = logging.getLogger(__name__)

# Default top-quality high-retention English voices
POPULAR_VOICES = {
    "christopher": "en-US-ChristopherNeural",  # Male, deep narrative, stoic / authoritative
    "guy": "en-US-GuyNeural",                  # Male, engaging, natural storytelling
    "jenny": "en-US-JennyNeural",              # Female, clear, modern, educational
    "ryan": "en-GB-RyanNeural",                # British Male, sophisticated documentary tone
    "sonia": "en-GB-SoniaNeural",              # British Female, crisp, articulate
}


async def _generate_voice_and_subtitles_async(
    text: str,
    output_audio_path: Path,
    output_srt_path: Optional[Path] = None,
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
        # SubMaker generate_subs provides formatted WebVTT / SRT cues
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
    pitch: str = "+0Hz"
) -> Tuple[Path, Optional[Path]]:
    """
    Synchronous wrapper for generating voiceover audio and synchronized subtitles.
    Cost: 100% Free (Edge-TTS uses Azure Neural Voice without API key or token limit).
    """
    return asyncio.run(
        _generate_voice_and_subtitles_async(
            text=text,
            output_audio_path=output_audio_path,
            output_srt_path=output_srt_path,
            voice=voice,
            rate=rate,
            pitch=pitch
        )
    )
