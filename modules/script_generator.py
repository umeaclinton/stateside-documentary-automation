import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class VideoScene(BaseModel):
    scene_number: int = Field(description="Order index of the scene (1, 2, 3...)")
    narration: str = Field(description="The spoken narration text for this specific scene")
    broll_keywords: List[str] = Field(
        description="2-3 specific visual search keywords for Pexels B-roll footage (e.g. ['man thinking dark mood', 'hourglass sand falling', 'chess strategy piece'])"
    )

class ShortScript(BaseModel):
    niche: str = Field(description="The topic niche of the video")
    title: str = Field(description="Catchy, high-CTR YouTube Shorts title including #Shorts (under 70 chars)")
    description: str = Field(description="Engaging description with relevant viral hashtags")
    tags: List[str] = Field(description="7 to 10 relevant YouTube tags")
    hook: str = Field(description="The opening 3-second hook designed to stop scrolling")
    full_narration: str = Field(description="The complete spoken voiceover text from beginning to end")
    scenes: List[VideoScene] = Field(description="Breakdown of scenes for dynamic visual pacing")


def generate_short_script(
    api_key: str,
    niche: str = "Psychology & Human Behavior",
    specific_topic: Optional[str] = None
) -> ShortScript:
    """
    Generates a high-retention 45-55 second YouTube Short script using the Gemini API.
    Uses structured JSON schema output to guarantee exact structure.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is required to generate video scripts.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an elite YouTube Shorts creator whose videos consistently get millions of views in the "{niche}" niche.

Task:
Create a complete, high-retention, 45 to 55-second faceless vertical YouTube Short script.
{f'Focus specifically on this topic: {specific_topic}' if specific_topic else 'Choose a fascinating, evergreen, mind-bending psychology/wisdom topic that will remain interesting for years.'}

Retention & Pacing Rules:
1. The Hook (0-3s): Must immediately interrupt the viewer's scroll. Use curiosity gap or counter-intuitive psychological facts. No "Hey guys", no introduction. Start immediately with the punch.
2. The Core Body (3-45s): 3 rapid, eye-opening psychological insights or life principles. Keep sentences short, punchy, and conversational.
3. The Outro / Loop (45-55s): Conclude with a provocative question or a closing line that flows naturally if the video loops.
4. Visual Pacing: Break the script into 5 to 8 short scenes (each 5-8 seconds long). For each scene, provide 2-3 cinematic, moody B-roll search queries that can be found on stock video platforms like Pexels (e.g. 'cinematic dark library', 'man walking alone night rain', 'intense eye reflection', 'stoic statue marble portrait').
5. Title: Must be click-worthy, suspenseful, under 65 characters, and end with #Shorts.
6. Narration: The `full_narration` MUST be the seamless combined narration of all scenes in order. Total words should be around 110-140 words (perfect for 45-55 seconds at normal speech rate).
"""

    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.8-flash"
    ]
    last_err = None

    for model_name in models_to_try:
        try:
            logger.info(f"Generating script using Gemini model: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ShortScript,
                    temperature=0.85,
                )
            )

            # Parse and validate response
            script_data = json.loads(response.text)
            short_script = ShortScript.model_validate(script_data)
            logger.info(f"Successfully generated script: '{short_script.title}'")
            return short_script

        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}. Trying next fallback...")
            last_err = e

    raise RuntimeError(f"All Gemini models failed to generate script: {last_err}")
