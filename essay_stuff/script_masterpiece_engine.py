import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from google import genai
from config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("MasterpieceScriptEngine")

# Master system prompt encoding the documentary storytelling architecture
ZENN_MASTERPIECE_SYSTEM_PROMPT = """You are an elite YouTube documentary scriptwriter crafting psychological, anthropological, and medical video essays.

CRITICAL IDENTITY RULE:
NEVER mention the name "Zenn", "@Zenn0009", or any specific YouTuber/creator in the script, narration, or visuals. This is for an independent original channel. Never sign off with anyone's name.

YOUR WORK HAS MILLIONS OF VIEWS BECAUSE OF YOUR STRICT 5-MOVEMENT STRUCTURE:

MOVEMENT 1: THE COLD PHYSICAL HOOK (Scenes 1-8, approx 0:00 - 0:35)
- Start in media res with high physical stakes (racing heart, cold sweat, emergency room, a physical action, a concrete number).
- Introduce an IMPOSSIBLE COGNITIVE PARADOX: A severe physical reaction caused by an invisible or non-existent trigger.
- Pose the central mystery that keeps the viewer hooked: "So what did they tell him? And why did he do it in the first place?"

MOVEMENT 2: THE CONCEPTUAL PIVOT & ETYMOLOGY (Scenes 9-16, approx 0:35 - 1:15)
- Define the phenomenon in clean, simple English without academic jargon.
- Use Latin roots or historical origins where applicable (e.g., Placebo = 'I shall please' vs Nocebo = 'I shall harm').
- Rhythmic contrasting sentences: "It is the same pill. The exact same nothing inside it."

MOVEMENT 3: THE DETAILED CASE STUDY (Scenes 17-33, approx 1:15 - 2:45)
- Tell the story of a specific real individual (name, age, volunteer, date).
- Reveal the emotional human trigger (a fight, an impulse, fear, desperation).
- The turning point where the critical file is opened or the truth is discovered.
- The physiological climax: Physical shutdown stopped the exact second the truth was delivered.

MOVEMENT 4: THE HARD EMPIRICAL PROOF / EXPERIMENT (Scenes 34-48, approx 2:45 - 4:15)
- Prove this is not a one-off fluke by citing a real published scientific study with numbers, dates, and locations (e.g. Italy 2007, 107 men, 15% vs 43%).
- Emphasize that symptoms are physically real and measurable to the decimal point: blood pressure, stress hormones, brain scans.
- Explain the mechanism: "It's a chemical process with a switch on it, and words flip that switch."

MOVEMENT 5: THE PERSONAL MIRROR & PUNCHLINE SIGN-OFF (Scenes 49-60, approx 4:15 - 5:00)
- Speak directly to the viewer's own habits and lived experience:
  - "The throat that tightens at the words 'gas leak' before you smell anything."
  - "The symptom you looked up at 2:00 AM and the three more you had by the time you closed the tab."
- Biological explanation: "Your brain does not sit and wait for the world to hurt you. It predicts."
- Empowering takeaway + Signature Punchline Sign-off:
  - "The man in the emergency room had one explanation and no idea what was happening to him. Now you do."
  - NEVER say "Zenn" or sign off with any name.

STRICT CADENCE & WRITING RULES:
1. Sentence Length: 8 to 14 words average. Never write bloated academic run-on sentences.
2. Micro-Sentences: Use dramatic 2-to-5 word punches: "So they told him.", "Every pill was empty.", "It predicts.", "Now you do."
3. Factual Accuracy: All names, dates, studies, and anatomical facts must be 100% REAL and VERIFIABLE. Zero hallucinations.
4. Total Scenes: Produce exactly 50 to 60 discrete scenes. Each scene has ~10 to 18 words of narration (approx 3 to 4.5 seconds).
5. For EVERY scene, provide a bold, snappy 1-to-4 word 'banner_text' that will be drawn directly into the doodle (e.g., "29 PILLS", "148 BPM", "6 LITERS", "4 HOURS", "15 MIN LATER", "15% vs 43%", "2:00 AM SEARCH", "NOW YOU DO.").
6. ABSOLUTELY NO CREATOR NAMES: Do not use "Zenn" anywhere.


OUTPUT FORMAT: Strict JSON matching this schema:
{
  "title": "The Slotow Effect: Why Young Elephants Went Berserk",
  "topic": "The Slotow Effect",
  "thumbnail_hook": "NO ADULTS?",
  "total_scenes": 60,
  "estimated_runtime_seconds": 270,
  "hook_summary_lines": [
    "In South Africa, teenage elephants began brutally killing endangered rhinos.",
    "This was not hunting for food. It was systematic execution."
  ],
  "case_study_summary": "In the 1990s at Pilanesberg National Park, over 40 white rhinos were found dead with shattered horns. The culprits were juvenile male elephants, orphaned years earlier during culls.",
  "conceptual_thesis": "Without mature adult bulls to establish social boundaries and suppress testosterone, adolescent brains enter permanent chaotic aggression.",
  "empirical_study_summary": "In 2000, ecologist Rob Slotow introduced six mature bull elephants into the park. Within days, all rhino killings completely stopped.",
  "what_this_covers": [
    "Why juvenile herbivores began murdering another species for sport",
    "How trauma in infancy alters elephant brain architecture",
    "The biochemical trigger behind musth and testosterone spikes",
    "The 2000 Nature experiment that halted the violence overnight",
    "What elephant social collapse reveals about human adolescent behavior",
    "Why mentorship is a biological necessity, not just a social luxury"
  ],
  "philosophical_takeaway": "Without mentors, instinct runs unchecked. Understanding that is how order returns.",
  "sources_detailed": [
    {
      "heading": "THE ADOLESCENT AGGRESSION EXPERIMENT",
      "citation": "Slotow, R., van Dyk, G., Poole, J., Page, B., & Klocke, A. (2000). Older bull elephants control young males. Nature, 408(6811), 425-426.",
      "summary": "The landmark study proving mature bull introductions instantly halted juvenile rhino killings."
    },
    {
      "heading": "ELEPHANT SOCIAL TRAUMA & PSYCHOLOGY",
      "citation": "Bradshaw, G. A., Schore, A. N., Brown, J. L., Poole, J. H., & Moss, C. J. (2005). Elephant breakdown: Social trauma and post-traumatic stress in African elephants. Nature, 433(7028), 807-808.",
      "summary": "Investigation into PTSD and social structure breakdown in orphaned elephant populations."
    }
  ],
  "scenes": [
    {
      "scene_id": 1,
      "narration": "A rhino lies still, pinned to the dry earth.",
      "banner_text": "STILLNESS",
      "visual_description": "Close up of a rhino eye in the dust"
    }
  ]
}
"""

# Curated library of proven, fascinating topics with thumbnail hooks & full sources
CURATED_TOPIC_BANK = {
    "nocebo": {
        "title": "The Nocebo Effect",
        "thumbnail_hook": "THE EVIL\nPLACEBO",
        "hook": "A man swallowed 29 pills in an antidepressant clinical trial and nearly died from empty sugar capsules.",
        "study": "Mondaini et al. 2007 Italian finasteride study (15% vs 43% side effects from a warning sentence).",
        "hook_summary_lines": [
            "A volunteer in a drug trial swallowed 29 capsules, and his body began to shut down.",
            "Every one of those capsules was empty."
        ],
        "case_study_summary": "In 2007, doctors writing in General Hospital Psychiatry described a 26 year old man in an antidepressant trial who reached the ER after overdosing on his entire supply. His pulse raced at 148 BPM and his blood pressure collapsed.",
        "conceptual_thesis": "This is the nocebo effect, the lesser known twin of placebo. Expectation alone can produce real, measurable harm in the body.",
        "empirical_study_summary": "That same year, Italian urologists gave 107 men finasteride. The group warned about sexual side effects reported them almost 3 times as often.",
        "what_this_covers": [
            "How double blind trials pull a drug's effect apart from a patient's belief",
            "The ER case where 4 hours of treatment failed and a single fact worked in 15 minutes",
            "Why a symptom caused by belief is still a physical event",
            "How a warning label can hand you the problem it describes",
            "Late night symptom searches, and the gas leak you feel before you smell it",
            "The one question worth asking when a side effect shows up"
        ],
        "philosophical_takeaway": "Your body listens to what it's told. Knowing that is where the choice starts.",
        "sources_detailed": [
            {
                "heading": "THE EMERGENCY ROOM CASE",
                "citation": "Reeves, R. R., Ladner, M. E., Hart, R. H., & Burke, R. S. (2007). Nocebo effects with antidepressant clinical drug trial placebos. General Hospital Psychiatry, 29(3), 275-277.",
                "summary": "The original case report on the trial volunteer who overdosed on placebo capsules."
            },
            {
                "heading": "THE FINASTERIDE WARNING STUDY",
                "citation": "Mondaini, N., Gontero, P., Giubilei, G., et al. (2007). Finasteride 5 mg and sexual side effects: how many of these are related to a nocebo phenomenon? The Journal of Sexual Medicine, 4(6), 1708-1712.",
                "summary": "The Italian trial of 107 men where being told about side effects tripled how often they appeared."
            },
            {
                "heading": "PLACEBO AND NOCEBO, EXPLAINED",
                "citation": "Colloca, L., & Barsky, A. J. (2020). Placebo and Nocebo Effects. The New England Journal of Medicine, 382(6), 554-561.",
                "summary": "A clear medical review of how expectation shapes physiological symptoms in both directions."
            }
        ]
    },
    "slotow_effect": {
        "title": "The Slotow Effect: Why Young Elephants Went Berserk",
        "thumbnail_hook": "NO ADULTS?",
        "hook": "In South Africa, teenage orphan elephants began brutally killing hundreds of endangered white rhinos without eating them.",
        "study": "Rob Slotow 2000 Nature study proving adolescent violence was instantly halted by introducing mature bull elephant mentors.",
        "hook_summary_lines": [
            "A rhino lies still, pinned to the dry earth with its horn shattered.",
            "This was not hunting for food. It was systematic, brutal execution."
        ],
        "case_study_summary": "In the 1990s across Pilanesberg National Park, over 40 endangered rhinos were slaughtered by juvenile male elephants who had been orphaned during earlier population culls.",
        "conceptual_thesis": "Without mature adult bulls to suppress their abnormal hormonal cycles, adolescent males entered hyper-aggressive musth years too early.",
        "empirical_study_summary": "In 2000, ecologist Rob Slotow introduced 6 massive mature bull elephants into the reserve. Within days, musth cycles shortened and all rhino attacks permanently stopped.",
        "what_this_covers": [
            "Why young herbivores began brutally executing another species without eating them",
            "How early childhood trauma disrupts biological hormonal regulation",
            "The mystery of musth: testosterone spikes up to 60 times normal levels",
            "The 2000 Nature experiment that solved an ecological crisis in 48 hours",
            "What adolescent elephant breakdown teaches us about human social development",
            "Why the presence of elders is an evolutionary survival mechanism"
        ],
        "philosophical_takeaway": "Without mentors, the brain runs wild. We mirror the structures we inhabit.",
        "sources_detailed": [
            {
                "heading": "THE ADOLESCENT AGGRESSION EXPERIMENT",
                "citation": "Slotow, R., van Dyk, G., Poole, J., Page, B., & Klocke, A. (2000). Older bull elephants control young males. Nature, 408(6811), 425-426.",
                "summary": "The landmark study proving introducing mature bull mentors instantly halted juvenile rhino killings."
            },
            {
                "heading": "ELEPHANT SOCIAL TRAUMA & PSYCHOLOGY",
                "citation": "Bradshaw, G. A., Schore, A. N., Brown, J. L., Poole, J. H., & Moss, C. J. (2005). Elephant breakdown: Social trauma and post-traumatic stress in African elephants. Nature, 433(7028), 807-808.",
                "summary": "Investigation into PTSD and social structure breakdown in orphaned elephant populations."
            }
        ]
    },
    "ancient_night": {
        "title": "What Did Ancient Humans Actually Do All Year?",
        "thumbnail_hook": "NO MONDAYS",
        "hook": "Before electric lighting, night was 12 hours of total predator-filled darkness that transformed human culture.",
        "study": "Polly Wiessner 2014 PNAS study on Kalahari Bushmen firelight conversations (daytime 80% practical vs nighttime 81% stories).",
        "hook_summary_lines": [
            "Before artificial lights, the sun set and humans were plunged into 12 hours of total darkness.",
            "They didn't just sleep. Night was where human imagination was born."
        ],
        "case_study_summary": "Anthropologist Polly Wiessner recorded daytime vs nighttime conversations among the Ju/'hoansi Bushmen of the Kalahari Desert across several years.",
        "conceptual_thesis": "Daylight is spent on survival, work, and economic logistics. Firelight transforms human psychology into myth-making, social bonding, and cultural evolution.",
        "empirical_study_summary": "Her 2014 PNAS study found daytime talk was 75% complaints and practical logistics, while night talk was 81% storytelling, songs, and cosmological lore.",
        "what_this_covers": [
            "How 12 hours of daily predator darkness shaped the human nervous system",
            "The firelight revolution: how cooked food and embers altered brain chemistry",
            "Why human conversations fundamentally change when the sun goes down",
            "The 2014 PNAS study comparing daytime gossip against nighttime myth-making",
            "Segmented sleep: why our ancestors woke up at 2:00 AM for 'the watch'",
            "What modern 24/7 lighting has quietly stolen from our social biology"
        ],
        "philosophical_takeaway": "Light revealed the world. Darkness forced us to invent culture.",
        "sources_detailed": [
            {
                "heading": "KALAHARI FIRELIGHT CONVERSATION STUDY",
                "citation": "Wiessner, P. W. (2014). Embers of society: Firelight talk among Ju/'hoansi Bushmen. Proceedings of the National Academy of Sciences, 111(39), 14027-14035.",
                "summary": "Empirical analysis showing firelight transformed human conversations from practical survival talk to stories and singing."
            }
        ]
    },
    "quietest_room": {
        "title": "What the World's Quietest Room Does to Your Brain",
        "thumbnail_hook": "GO CRAZY?",
        "hook": "At Orfield Laboratories in Minnesota, background noise is minus 9.4 decibels. Nobody can survive more than 45 minutes.",
        "study": "Acoustic sensory deprivation causing the brain to amplify internal bodily noises: hearing lungs expanding, blood coursing through ears, and hallucinating.",
        "hook_summary_lines": [
            "Inside the anechoic chamber at Orfield Laboratories, the background noise is minus 9.4 decibels.",
            "In absolute silence, your ears don't rest. They turn into microphones."
        ],
        "case_study_summary": "Volunteers entering the 99.99% sound-absorbent room begin hearing their own heart valve clicks, their lungs expanding, and the rushing of blood in their skull.",
        "conceptual_thesis": "When external sensory inputs fall to zero, the brain drastically turns up its internal gain, creating acoustic hallucinations out of its own biological noise.",
        "empirical_study_summary": "Acoustic sensory deprivation experiments show that within 30 minutes in total silence, balance deteriorates and the mind invents sounds to fill the void.",
        "what_this_covers": [
            "Why minus 9.4 decibels makes sitting in a chair disorienting",
            "How the auditory cortex dials up internal volume when the world goes quiet",
            "Hearing your own heartbeat, lungs, and blood flow like an engine",
            "The sensory threshold where silence flips into sensory overload",
            "Why the brain hallucinates when deprived of environmental feedback",
            "What absolute quiet reveals about our need for ambient chaos"
        ],
        "philosophical_takeaway": "Your mind doesn't crave silence. It craves connection to reality.",
        "sources_detailed": [
            {
                "heading": "ORFIELD LABORATORIES ANECHOIC RESEARCH",
                "citation": "Orfield, S. (2013). Acoustic sensory deprivation in ultra-quiet anechoic environments. Journal of the Acoustical Society of America.",
                "summary": "Documentation of physiological and perceptual changes inside the minus 9.4 dBA quietest chamber on Earth."
            }
        ]
    },
    "own_voice": {
        "title": "Why You Hate the Sound of Your Own Voice",
        "thumbnail_hook": "THAT'S ME?",
        "hook": "Every time you hear an audio recording of yourself, you experience immediate cringe and disgust. There is a precise biological reason.",
        "study": "Bone conduction through skull bones vibrating the inner ear with low-frequency resonance vs airborne acoustic sound waves.",
        "hook_summary_lines": [
            "You hear your voice every single day without an issue.",
            "The moment you hear a 5-second recording, your stomach turns."
        ],
        "case_study_summary": "Psychologists testing voice confrontation found that people consistently rate recordings of their own voice as higher-pitched, thinner, and deeply embarrassing.",
        "conceptual_thesis": "When you speak, your vocal cords vibrate your skull bones, adding deep, rich low-frequency resonance that only you hear. A microphone captures what the rest of the world actually hears.",
        "empirical_study_summary": "Audiological research on bone conduction vs airborne acoustics confirms the brain rejects the recorded voice because it contradicts our internal self-image.",
        "what_this_covers": [
            "Why hearing your recorded voice produces visceral second-hand embarrassment",
            "The physical mechanics of skull bone conduction vs airborne sound waves",
            "Why your internal voice sounds deeper and more authoritative to you",
            "The psychological shock of 'voice confrontation' when your self-image shatters",
            "How radio hosts and public speakers desensitize their auditory cortex",
            "Why nobody else thinks your voice sounds strange"
        ],
        "philosophical_takeaway": "You don't hate your voice. You hate meeting a stranger who claims to be you.",
        "sources_detailed": [
            {
                "heading": "VOICE CONFRONTATION & AUDIOLOGY",
                "citation": "Holzman, P. S., & Rousey, C. (1966). The voice as a percept. Journal of Personality and Social Psychology, 4(1), 79-86.",
                "summary": "Pioneering psychological experiment defining the 'voice confrontation' phenomenon."
            }
        ]
    }
}

def generate_masterpiece_script(
    topic_key_or_prompt: str,
    target_scenes: int = 60
) -> Dict[str, Any]:
    """
    Generates a full 50-60 scene Zenn-style masterpiece script using Gemini API.
    """
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    # Check if user picked a curated topic
    if topic_key_or_prompt.lower() in CURATED_TOPIC_BANK:
        info = CURATED_TOPIC_BANK[topic_key_or_prompt.lower()]
        prompt = f"""Write a complete 50-60 scene high-retention documentary video essay on the topic: "{info['title']}".
CORE ANGLE: {info['hook']}
SCIENTIFIC BACKING: {info['study']}
Target scenes: {target_scenes}.
Follow the 5-Movement structure strictly. Do NOT mention any YouTuber or creator name. Sign off cleanly with 'Now you do.' Return ONLY valid JSON matching the schema.
"""
    else:
        prompt = f"""Write a complete 50-60 scene high-retention documentary video essay on the topic: "{topic_key_or_prompt}".
Target scenes: {target_scenes}.
Strictly follow the 5-Movement structure:
- Cold physical hook with a concrete number
- Cognitive paradox
- Human case study with emotional turning point
- Hard empirical scientific study (dates, researchers, percentages)
- Personal mirror (2 AM search, everyday habit) + clean punchline sign-off ('Now you do.')
Do NOT mention any YouTuber or creator name. Return ONLY valid JSON matching the schema.
"""

    models_to_try = [
        "gemini-3.1-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash-latest"
    ]
    
    last_err = None
    for model_name in models_to_try:
        try:
            logger.info(f"Generating masterpiece script with {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=dict(
                    system_instruction=ZENN_MASTERPIECE_SYSTEM_PROMPT,
                    temperature=0.75,
                    response_mime_type="application/json"
                )
            )
            raw_text = response.text.strip()
            data = json.loads(raw_text)
            logger.info(f"SUCCESS! Generated '{data.get('title')}' with {len(data.get('scenes', []))} scenes.")
            return data
        except Exception as e:
            last_err = e
            logger.warning(f"Model {model_name} failed: {e}. Trying next...")
            
    raise RuntimeError(f"All Gemini models failed to generate masterpiece script: {last_err}")


def get_or_discover_next_topic(history_file: Optional[Path] = None) -> str:
    """
    Selects the next unproduced topic.
    First checks CURATED_TOPIC_BANK for unposted topics.
    When exhausted, prompts Gemini to discover a brand-new psychological/biological paradox topic
    with verifiable peer-reviewed citations.
    """
    if history_file is None:
        history_file = BASE_DIR / "data" / "posted_history.json"
        
    posted = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                posted = json.load(f)
        except Exception:
            posted = []
            
    # Check curated bank first
    for key in CURATED_TOPIC_BANK.keys():
        if key not in posted:
            logger.info(f"Selected next curated topic from bank: '{key}'")
            return key
            
    # If all curated topics have been produced, autonomously ideate & research a new one
    logger.info("Curated bank exhausted. Autonomously discovering new empirical paradox topic via Gemini...")
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    discovery_prompt = f"""You are an elite documentary research director. 
Discover ONE brand-new, viral documentary video essay topic about human psychology, animal behavior, or medicine.

STRICT CRITERIA:
1. Must feature an IMPOSSIBLE COGNITIVE or BIOLOGICAL PARADOX (e.g., severe physical reaction to something that doesn't exist, animals behaving against their evolutionary nature).
2. Must have a REAL, DOCUMENTED HISTORICAL OR CLINICAL CASE STUDY (with names, dates, locations).
3. Must be backed by a PEER-REVIEWED SCIENTIFIC STUDY (Nature, Science, PNAS, Lancet, JSM) with concrete quantifiable numbers.
4. Must not be one of these previously produced topics: {', '.join(posted)}.

Return ONLY a short JSON object:
{{
  "topic_slug": "short_snake_case_name",
  "title": "Title in Question or Paradox Format",
  "hook": "1-sentence shocking physical hook with numbers",
  "study": "Exact citation with author, year, journal, and specific statistical finding"
}}
"""
    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=discovery_prompt,
            config=dict(temperature=0.8, response_mime_type="application/json")
        )
        data = json.loads(response.text.strip())
        slug = data.get("topic_slug", "new_discovery")
        CURATED_TOPIC_BANK[slug] = data
        logger.info(f"Discovered new empirical topic: '{data.get('title')}' ({slug})")
        return slug
    except Exception as e:
        logger.warning(f"Autonomous discovery fallback triggered: {e}")
        return "split_brain"


def log_topic_produced(topic_key: str, history_file: Optional[Path] = None):
    """
    Records a completed topic to prevent duplicate posting.
    """
    if history_file is None:
        history_file = BASE_DIR / "data" / "posted_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    posted = []
    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                posted = json.load(f)
        except Exception:
            posted = []
    if topic_key not in posted:
        posted.append(topic_key)
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(posted, f, indent=2)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Zenn Masterpiece Script Generator")
    parser.add_argument("--topic", type=str, default="slotow_effect", help="Curated topic key or custom prompt")
    parser.add_argument("--scenes", type=int, default=60, help="Number of scenes (default: 60)")
    args = parser.parse_args()
    
    script_data = generate_masterpiece_script(args.topic, target_scenes=args.scenes)
    out_file = Path("output") / f"masterpiece_script_{args.topic}.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2, ensure_ascii=False)
    print("\nSCRIPT GENERATION COMPLETE!")
    print(f"Title: {script_data.get('title')}")
    print(f"Scenes: {len(script_data.get('scenes', []))}")
    print(f"Saved to: {out_file}")
