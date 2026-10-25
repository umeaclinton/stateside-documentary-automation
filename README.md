# 🎬 Zenn-Style Documentary Video Essay Engine

An autonomous, zero-cost production pipeline for generating, illustrating, voicing, and compiling high-retention psychological, scientific, and historical documentary video essays modeled after the exact narrative and visual aesthetic of **Zenn (@Zenn0009)**.

---

## 🏛️ Narrative Architecture: The 5-Movement Structure

Every video follows Zenn's signature storytelling formula:

1. **Movement 1: The Cold Physical Hook (0:00 - 0:35)**
   - Starts *in media res* with high physical stakes (racing heart, cold sweat, emergency room, a physical action, a concrete number).
   - Introduces an impossible cognitive paradox: a severe physical reaction caused by an invisible trigger.
2. **Movement 2: The Conceptual Pivot & Etymology (0:35 - 1:15)**
   - Jargon-free definition in plain English (e.g. Latin roots: *Placebo* = "I shall please" vs *Nocebo* = "I shall harm").
3. **Movement 3: The Detailed Human Case Study (1:15 - 2:45)**
   - A specific real individual's story (name, age, volunteer, date) with emotional turning points.
4. **Movement 4: Hard Empirical Proof & Peer-Reviewed Science (2:45 - 4:15)**
   - Hard scientific backing citing published studies (*Nature*, *PNAS*, *General Hospital Psychiatry*) with real dates, sample sizes, and percentages.
5. **Movement 5: The Personal Mirror & Punchline Sign-Off (4:15 - End)**
   - Connects directly to the viewer's everyday habits (2 AM Google search, tight throat).
   - Signature punchline: *"The man in the emergency room had one explanation and no idea what was happening to him. Now you do."*

---

## 🎨 Visual & Auditory Standards

- **Visuals:** Pure white (`#FFFFFF`) 1920×1080 Full HD canvas.
- **Linework:** Hand-drawn wobbly ink outlines (thickness: 5–8px) with expressive stickman doodles.
- **Stability:** **100% rock-solid static frames.** No subpixel digital zooms or jitter.
- **Pacing:** Rapid visual cuts every **2.0 to 3.5 seconds** (50–60 scenes per video).
- **Integrated Text Banners:** High-impact bold callouts drawn directly into each doodle (e.g. `29 PILLS`, `148 BPM`, `15 MIN LATER`, `NOW YOU DO.`).
- **Narrator:** ElevenLabs **George** (`JBFqnCBsd6RMkjVDRZzb`) using `eleven_turbo_v2_5`, with seamless automatic fallback to `Edge-TTS` (`en-US-ChristopherNeural`).
- **Sound Design:** Layered with a 55Hz + 110Hz sub-bass atmospheric tension drone at -24dB (`weight: 0.10`).

---

## 🚀 Quick Start & CLI Usage

### Generate a Video Essay
```bash
# Run with a curated topic:
.\.venv\Scripts\python.exe essay_stuff\generate_essay.py --topic slotow_effect

# Or generate with any custom prompt:
.\.venv\Scripts\python.exe essay_stuff\generate_essay.py --topic "Why You Wake Up at 3:00 AM" --scenes 55
```

### Curated Topic Library
- `slotow_effect` — Why adolescent elephants went berserk (*Slotow 2000, Nature*)
- `nocebo` — How words can poison the body (*Mondaini 2007, JSM*)
- `ancient_night` — What humans did in 12 hours of total darkness (*Wiessner 2014, PNAS*)
- `minnesota_starvation` — The psychology of starvation (*Keys 1944*)
- `quietest_room` — Acoustic deprivation at minus 9.4 decibels
- `own_voice` — The acoustics of bone conduction
- `uncanny_valley` — Evolutionary dread mechanisms
- `split_brain` — Two minds inside one skull (*Sperry Nobel Prize*)

---

## 📁 Workspace Directory Structure

```text
YT video automation/
├── essay_stuff/
│   ├── BLUEPRINT.md                 # Locked visual, pacing, and audio specifications
│   ├── generate_essay.py            # Master CLI orchestrator (Script -> Voice -> Doodles -> Concat -> Drone)
│   ├── script_masterpiece_engine.py # 5-Movement Gemini script generator + Curated Topic Bank
│   ├── visual_masterpiece_engine.py # Rock-solid 1080p static doodle generator with bold banners
│   └── nocebo_full_production.py    # Reference 60-scene production file
├── modules/
│   └── youtube_uploader.py          # YouTube Data API v3 publishing
├── output/
│   ├── essays/                      # Generated production packages (audio, frames, clips, masters)
│   └── nocebo_full/                 # 4m 32s Nocebo master video
├── credentials/
│   └── credentials_vault.md         # Stored API configurations
├── config/
│   └── settings.py                  # Environment settings
├── setup_youtube_auth.py            # OAuth token initialization
├── requirements.txt                 # Clean minimal dependencies
└── README.md                        # Documentation
```
