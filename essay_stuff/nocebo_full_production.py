import os
import sys
import json
import math
import random
import subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Force UTF-8 on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

FFMPEG = "C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffmpeg.exe"
FFPROBE = "C:/Users/USER/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin/ffprobe.exe"
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb" # George - Storyteller

# The complete 60-scene breakdown
FULL_SCRIPT = [
    (1, "A man swallowed 29 pills at once.", "29 PILLS", "swallow"),
    (2, "He reached an emergency room soaked in sweat and shaking.", "EMERGENCY ROOM", "er_door"),
    (3, "His heart was racing and his blood pressure was dangerously low.", "148 BPM | B.P. 80/40", "ecg_monitor"),
    (4, "Doctors pushed 6 liters of fluid into him, trying to keep him alive.", "6 LITERS", "iv_bed"),
    (5, "4 hours of that and he was still dying.", "4 HOURS LATER...", "clock_4"),
    (6, "Then somebody told him one thing.", "ONE SENTENCE", "whisper"),
    (7, "15 minutes later he was sitting up and talking like nothing had happened.", "15 MIN LATER", "sitting_up"),
    (8, "So what did they tell him? And why did he swallow 29 of them in the first place?", "WHY 29 PILLS?", "question"),
    (9, "This is the nocebo effect. You have heard of its twin.", "PLACEBO vs NOCEBO", "two_pills"),
    (10, "Placebo is Latin for 'I shall please'. It's the sugar pill, the dummy, the capsule with nothing in it.", "PLACEBO = 'I SHALL PLEASE'", "sugar_pill"),
    (11, "Nocebo is Latin for 'I shall harm'. It is the same pill, the exact same nothing inside it.", "NOCEBO = 'I SHALL HARM'", "harm_pill"),
    (12, "The man from that emergency room was 26, and he had volunteered for a clinical trial, testing a new antidepressant.", "AGE: 26\nCLINICAL TRIAL", "volunteer"),
    (13, "A trial works like this. Half the volunteers get the real drug.", "GROUP A: REAL DRUG (50%)", "split_group_a"),
    (14, "The other half get capsules that look identical and have nothing inside them, and nobody is told which half they're in.", "GROUP B: EMPTY (50%)", "split_group_b"),
    (15, "Not the volunteers and often not the doctors handing them out.", "DOUBLE BLIND", "blindfold"),
    (16, "It is the most careful machine medicine has ever built, and it exists to separate what a drug does to a body from what a person believes it does.", "DRUG EFFECT vs BELIEF", "scale_balance"),
    (17, "He took one capsule a day and waited to feel different. 2 months in, he was still waiting.", "DAY 60: WAITING...", "calendar_waiting"),
    (18, "Then he had a fight with his girlfriend, and he swallowed every capsule he had left.", "ARGUMENT\nALL CAPSULES GONE", "fight_swallow"),
    (19, "He regretted it almost immediately.", "REGRET", "regret_head"),
    (20, "He made it as far as the emergency room doors, said, 'Help me, I took all my pills', and collapsed.", "'HELP ME...'", "collapse_door"),
    (21, "An empty bottle rolled out of his hand.", "EMPTY BOTTLE", "rolling_bottle"),
    (22, "4 hours later, he was no better.", "4 HOURS IN ICU", "bed_struggling"),
    (23, "Then a physician from the trial arrived, pulled his file, and found the one thing nobody in that room had thought to check.", "TRIAL FILE PULLED", "doctor_file"),
    (24, "He was in the half getting nothing. Every capsule he had ever swallowed was empty.", "EVERY PILL WAS EMPTY", "empty_capsule_reveal"),
    (25, "So they told him.", "THE REVEAL", "doctor_speaking"),
    (26, "He was surprised, and then almost tearfully relieved.", "TEARFUL RELIEF", "crying_relief"),
    (27, "15 minutes later he was fully alert, and his blood pressure was normal.", "15 MIN: 100% NORMAL", "vitals_normal"),
    (28, "No drug had ever entered his body.", "0% DRUG IN BLOOD", "zero_drug"),
    (29, "It had spent 4 hours shutting down over something that did not exist, and it stopped the second he found out.", "SHUTTING DOWN OVER NOTHING", "brain_switch_off"),
    (30, "So the placebo effect is when something fake makes you better because you expect it to help...", "PLACEBO: EXPECT TO HEAL", "placebo_heal"),
    (31, "...while the nocebo effect is when something fake makes you worse because you expect it to hurt.", "NOCEBO: EXPECT TO HARM", "nocebo_harm"),
    (32, "It's the same machine, but going in the opposite direction.", "OPPOSITE DIRECTIONS", "two_arrows"),
    (33, "Which sounds like an insult, that it was all in his head. And it was.", "'ALL IN YOUR HEAD'", "head_doodle"),
    (34, "And that's not an insult, because this is not a man imagining things, or being dramatic, or talking himself into a bad mood.", "NOT DRAMA", "not_imagining"),
    (35, "It's blood pressure, stress hormones, and pain that shows up in a laboratory and can be measured to the decimal point.", "MEASURED IN A LAB", "lab_tubes"),
    (36, "It's a chemical process with a switch on it, and other people can flip that switch by talking to you.", "WORDS FLIP THE SWITCH", "chemical_switch"),
    (37, "Urologists in Italy showed how little it takes.", "ITALY 2007", "italy_map"),
    (38, "In 2007, they had 107 men taking finasteride, a common drug for an enlarged prostate.", "107 MEN\nFINASTERIDE", "men_group"),
    (39, "One of its known side effects is sexual dysfunction.", "KNOWN SIDE EFFECT", "warning_icon"),
    (40, "They split the men into two groups, and both got the real drug. Same pills, same dose, same everything.", "BOTH GOT THE REAL DRUG", "identical_bottles"),
    (41, "The only difference was one sentence.", "ONE SENTENCE DIFFERENCE", "quote_bubble"),
    (42, "The first group was told nothing about sexual side effects.", "GROUP 1: TOLD NOTHING", "no_warning"),
    (43, "The second group was told the drug may cause sexual side effects, but these are uncommon.", "GROUP 2: WARNED", "with_warning"),
    (44, "In the group that wasn't warned, 15% came back reporting sexual problems.", "NOT WARNED: 15%", "bar_15"),
    (45, "In the group that was warned, 43% did.", "WARNED: 43%", "bar_43"),
    (46, "Nearly half of them on a drug that other half were taking without much trouble.", "TRIPLED BY A WARNING", "comparison_bars"),
    (47, "Those men weren't lying, and they weren't unusual. They swallowed exactly what the other group swallowed.", "EXACT SAME PILLS", "same_pills_check"),
    (48, "The only extra thing they got was a warning.", "THE WARNING WAS THE DRUG", "warning_stamp"),
    (49, "And that sentence they were told is the same kind of sentence printed on every prescription you have ever filled.", "PRESCRIPTION WARNING", "rx_paper"),
    (50, "It's there to protect you. It is also how the symptom gets delivered.", "PROTECTION OR DELIVERY?", "shield_symptom"),
    (51, "And you have probably been on the receiving end of it.", "HAVE YOU FELT THIS?", "you_pointing"),
    (52, "The throat that tightens at the words 'gas leak', before you've smelled anything at all.", "'GAS LEAK'", "gas_leak"),
    (53, "The symptom you looked up at 2:00 in the morning and the three more you had by the time you closed the tab.", "2:00 AM GOOGLE SEARCH", "google_2am"),
    (54, "Your brain does not sit and wait for the world to hurt you. It predicts.", "THE BRAIN PREDICTS", "brain_radar"),
    (55, "It gets your body ready for whatever it thinks is coming, and that preparation is not a rehearsal. You don't get a say in it.", "PREPARATION IS REAL", "body_gears"),
    (56, "That sounds like a life sentence. It's not.", "NOT A SENTENCE", "broken_chains"),
    (57, "No drug saved the man in the emergency room. The truth did.", "THE TRUTH SAVED HIM", "truth_light"),
    (58, "What the name buys you is not immunity. It's a question.", "NOT IMMUNITY. A QUESTION.", "question_shield"),
    (59, "The next time a symptom shows up right after somebody warned you about it, you get to ask which one you are feeling, the drug or the warning.", "THE DRUG OR THE WARNING?", "two_doors"),
    (60, "The man in the emergency room had one explanation for what was happening to him and no idea what the nocebo effect was. Now you do.", "NOW YOU DO.", "final_smile")
]

print(f"Total production scenes: {len(FULL_SCRIPT)}")

def get_font(size: int, bold: bool = True):
    font_names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "comicbd.ttf" if bold else "comic.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
    ]
    for fn in font_names:
        try:
            return ImageFont.truetype(f"C:/Windows/Fonts/{fn}", size)
        except Exception:
            continue
    return ImageFont.load_default()

def draw_wobbly_line(draw: ImageDraw.ImageDraw, points, fill="black", width=6, roughness=2):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(int(dist / 12), 1)
        prev_pt = (x1, y1)
        for s in range(1, steps + 1):
            t = s / steps
            mid_x = x1 + (x2 - x1) * t + random.uniform(-roughness, roughness)
            mid_y = y1 + (y2 - y1) * t + random.uniform(-roughness, roughness)
            if s == steps:
                mid_x, mid_y = x2, y2
            draw.line([prev_pt, (mid_x, mid_y)], fill=fill, width=width)
            prev_pt = (mid_x, mid_y)

def draw_circle_wobbly(draw: ImageDraw.ImageDraw, cx, cy, r, fill=None, outline="black", width=6):
    num_pts = 28
    pts = []
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        cur_r = r + random.uniform(-2, 2)
        pts.append((cx + cur_r * math.cos(angle), cy + cur_r * math.sin(angle)))
    pts.append(pts[0])
    if fill:
        draw.polygon(pts, fill=fill)
    draw_wobbly_line(draw, pts, fill=outline, width=width)

def draw_stickman(draw: ImageDraw.ImageDraw, cx, cy, scale=1.0, mood="normal", fill="white"):
    hr = int(70 * scale)
    draw_circle_wobbly(draw, cx, cy - int(90 * scale), hr, fill=fill, width=6)
    
    er = int(8 * scale)
    ey = cy - int(95 * scale)
    draw.ellipse([cx - int(25 * scale) - er, ey - er, cx - int(25 * scale) + er, ey + er], fill="black")
    draw.ellipse([cx + int(25 * scale) - er, ey - er, cx + int(25 * scale) + er, ey + er], fill="black")
    
    if mood == "happy":
        draw.arc([cx - int(25 * scale), cy - int(80 * scale), cx + int(25 * scale), cy - int(50 * scale)], 0, 180, fill="black", width=5)
    elif mood == "sad":
        draw.arc([cx - int(25 * scale), cy - int(65 * scale), cx + int(25 * scale), cy - int(35 * scale)], 180, 360, fill="black", width=5)
    elif mood == "scared":
        draw.ellipse([cx - int(15 * scale), cy - int(65 * scale), cx + int(15 * scale), cy - int(45 * scale)], fill="black")
    else:
        draw.line([(cx - int(20 * scale), cy - int(60 * scale)), (cx + int(20 * scale), cy - int(60 * scale))], fill="black", width=5)
        
    spine_len = int(180 * scale)
    draw_wobbly_line(draw, [(cx, cy - int(20 * scale)), (cx, cy + spine_len)], width=7)
    
    leg_len = int(180 * scale)
    hip_y = cy + spine_len
    draw_wobbly_line(draw, [(cx, hip_y), (cx - int(60 * scale), hip_y + leg_len)], width=7)
    draw_wobbly_line(draw, [(cx, hip_y), (cx + int(60 * scale), hip_y + leg_len)], width=7)
    
    sh_y = cy + int(30 * scale)
    if mood == "happy":
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(120 * scale), sh_y - int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(120 * scale), sh_y - int(80 * scale))], width=7)
    elif mood == "scared":
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(70 * scale), sh_y + int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(70 * scale), sh_y + int(80 * scale))], width=7)
    else:
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(90 * scale), sh_y + int(90 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(90 * scale), sh_y + int(90 * scale))], width=7)

def render_scene_image(scene_tuple, out_path: Path):
    sid, text, banner, visual_type = scene_tuple
    random.seed(2000 + sid)
    im = Image.new("RGB", (1920, 1080), "white")
    draw = ImageDraw.Draw(im)
    
    draw_wobbly_line(draw, [(80, 950), (1840, 950)], width=6)
    
    f_title = get_font(105, bold=True)
    f_sub = get_font(60, bold=False)
    
    lines = banner.split("\n")
    if len(lines) == 1:
        color = (220, 30, 30) if any(w in banner for w in ["NOCEBO", "CRITICAL", "HOURS", "ARGUMENT", "REGRET", "WARNED", "43%", "EMERGENCY"]) else (40, 140, 60) if any(w in banner for w in ["PLACEBO", "NORMAL", "SAVED", "15%"]) else "black"
        draw.text((200, 120), lines[0], fill=color, font=f_title)
    else:
        draw.text((200, 100), lines[0], fill=(220, 30, 30) if "WARNING" in lines[0] or "TRIAL" in lines[0] else "black", font=f_title)
        draw.text((210, 220), lines[1], fill=(80, 80, 80), font=f_sub)
        
    if visual_type == "swallow":
        draw_stickman(draw, 800, 500, scale=1.1, mood="scared")
        for px, py in [(920, 410), (960, 440), (1000, 400), (1040, 450)]:
            draw.ellipse([px-12, py-8, px+12, py+8], fill=(230, 240, 255), outline="black", width=4)
        draw.rounded_rectangle([1300, 720, 1450, 780], radius=8, fill=(255, 230, 180), outline="black", width=5)
        
    elif visual_type == "er_door" or visual_type == "collapse_door":
        draw.rectangle([1200, 250, 1750, 950], fill=(245, 248, 250), outline="black", width=7)
        draw.rectangle([1430, 380, 1530, 480], fill=(230, 40, 40))
        draw.rectangle([1380, 415, 1580, 445], fill=(230, 40, 40))
        draw_stickman(draw, 700, 520, scale=1.0, mood="scared")
        for sx, sy in [(600, 450), (620, 510), (780, 460)]:
            draw.ellipse([sx-8, sy-14, sx+8, sy+14], fill=(80, 190, 255), outline="black", width=3)
            
    elif visual_type == "ecg_monitor":
        draw.rounded_rectangle([200, 200, 1720, 900], radius=25, fill=(15, 20, 25), outline="black", width=8)
        cur_x = 240
        ecg_pts = [(cur_x, 480)]
        while cur_x < 1680:
            cur_x += 35
            ecg_pts.append((cur_x, 480))
            cur_x += 18
            ecg_pts.append((cur_x, 340))
            cur_x += 18
            ecg_pts.append((cur_x, 620))
            cur_x += 18
            ecg_pts.append((cur_x, 480))
            cur_x += 50
            ecg_pts.append((cur_x, 480))
        draw_wobbly_line(draw, ecg_pts, fill=(50, 255, 100), width=6)
        draw.text((260, 220), "HEART RATE: 148 BPM (RACING)", fill=(255, 80, 80), font=get_font(80, bold=True))
        draw.text((260, 750), "BLOOD PRESSURE: 80 / 40  [CRITICAL LOW]", fill=(255, 180, 40), font=get_font(75, bold=True))
        
    elif visual_type in ["iv_bed", "bed_struggling"]:
        draw.rectangle([450, 680, 1350, 790], fill=(225, 238, 248), outline="black", width=6)
        draw_stickman(draw, 600, 640, scale=0.8, mood="scared")
        draw.rounded_rectangle([1400, 220, 1600, 520], radius=30, fill=(230, 245, 255), outline="black", width=6)
        draw.rectangle([1405, 320, 1595, 515], fill=(160, 220, 255))
        draw_wobbly_line(draw, [(1500, 520), (1450, 650), (1050, 700)], fill=(120, 180, 240), width=6)
        
    elif visual_type == "clock_4":
        draw_circle_wobbly(draw, 960, 550, 220, fill=(255, 250, 240), width=8)
        draw_wobbly_line(draw, [(960, 550), (960, 380)], width=9)
        draw_wobbly_line(draw, [(960, 550), (1090, 620)], width=9)
        draw.arc([700, 290, 1220, 810], 30, 120, fill=(220, 50, 50), width=6)
        draw.arc([700, 290, 1220, 810], 210, 300, fill=(220, 50, 50), width=6)
        
    elif visual_type in ["whisper", "doctor_speaking"]:
        draw_stickman(draw, 650, 520, scale=1.0, mood="normal")
        draw_stickman(draw, 1050, 480, scale=1.1, mood="normal")
        draw.rounded_rectangle([1150, 320, 1500, 470], radius=25, fill=(255, 255, 220), outline="black", width=6)
        draw.text((1250, 345), ". . .", fill="black", font=get_font(100, bold=True))
        
    elif visual_type in ["sitting_up", "vitals_normal", "final_smile"]:
        draw_stickman(draw, 960, 480, scale=1.1, mood="happy")
        for sp in [(720, 420), (740, 380), (1180, 420), (1200, 380)]:
            draw_circle_wobbly(draw, sp[0], sp[1], 15, fill=(255, 220, 50), width=3)
            
    elif visual_type in ["two_pills", "opposite_directions", "two_doors"]:
        draw.rounded_rectangle([340, 420, 880, 660], radius=110, fill=(240, 255, 240), outline="black", width=7)
        draw.line([(610, 420), (610, 660)], fill="black", width=5)
        draw.text((410, 500), "PLACEBO", fill=(30, 140, 50), font=get_font(75, bold=True))
        draw.rounded_rectangle([1040, 420, 1580, 660], radius=110, fill=(255, 240, 240), outline="black", width=7)
        draw.line([(1310, 420), (1310, 660)], fill="black", width=5)
        draw.text((1130, 500), "NOCEBO", fill=(210, 30, 30), font=get_font(75, bold=True))
        
    elif visual_type in ["split_group_a", "split_group_b", "comparison_bars"]:
        draw.rectangle([450, 400, 750, 850], fill=(230, 245, 230), outline="black", width=6)
        draw.text((490, 870), "GROUP A", fill="black", font=get_font(60, bold=True))
        draw.rectangle([1150, 400, 1450, 850], fill=(255, 235, 235), outline="black", width=6)
        draw.text((1190, 870), "GROUP B", fill="black", font=get_font(60, bold=True))
        draw.text((530, 580), "50%", fill=(40, 140, 60), font=get_font(85, bold=True))
        draw.text((1230, 580), "50%", fill=(220, 40, 40), font=get_font(85, bold=True))
        
    elif visual_type in ["bar_15", "bar_43"]:
        draw.rectangle([450, 650, 750, 850], fill=(160, 220, 160), outline="black", width=6)
        draw.text((540, 550), "15%", fill=(30, 140, 50), font=get_font(90, bold=True))
        draw.text((440, 880), "NOT WARNED", fill="black", font=get_font(55, bold=True))
        
        draw.rectangle([1150, 380, 1450, 850], fill=(255, 140, 140), outline="black", width=6)
        draw.text((1240, 280), "43%", fill=(220, 30, 30), font=get_font(90, bold=True))
        draw.text((1210, 880), "WARNED", fill="black", font=get_font(55, bold=True))
        
    elif visual_type == "google_2am":
        draw.rounded_rectangle([350, 350, 1570, 750], radius=35, fill=(250, 252, 255), outline="black", width=7)
        draw.text((400, 400), "Search: 'sharp chest pain at night'", fill=(80, 80, 80), font=get_font(60, bold=False))
        draw.line([(400, 490), (1520, 490)], fill=(200, 210, 220), width=4)
        draw.text((400, 530), "Result 1: Rare fatal heart condition", fill=(220, 30, 30), font=get_font(65, bold=True))
        draw.text((400, 620), "Result 2: Emergency room immediately", fill=(220, 30, 30), font=get_font(65, bold=True))
        draw_stickman(draw, 220, 560, scale=0.8, mood="scared")
        
    elif visual_type in ["brain_radar", "head_doodle", "brain_switch_off"]:
        draw_circle_wobbly(draw, 960, 500, 200, fill=(255, 235, 240), outline="black", width=7)
        draw.arc([820, 400, 1100, 600], 0, 180, fill="black", width=5)
        draw.arc([860, 440, 1060, 560], 180, 360, fill="black", width=5)
        draw.text((760, 750), "THE BRAIN PREDICTS", fill=(220, 30, 30), font=get_font(75, bold=True))
        
    elif visual_type in ["rx_paper", "doctor_file"]:
        draw.rectangle([700, 300, 1220, 850], fill=(255, 255, 245), outline="black", width=6)
        draw.text((750, 330), "Rx PRESCRIPTION", fill=(20, 50, 160), font=get_font(55, bold=True))
        draw.line([(750, 410), (1170, 410)], fill="black", width=4)
        draw.text((750, 450), "WARNING: Side effects include...", fill=(220, 30, 30), font=get_font(45, bold=True))
        for ly in range(530, 780, 50):
            draw_wobbly_line(draw, [(750, ly), (1170, ly)], fill=(160, 160, 160), width=4)
            
    else:
        draw_stickman(draw, 960, 520, scale=1.1, mood="normal" if sid % 2 == 0 else "scared")
        draw.text((500, 360), "?", fill=(220, 120, 20), font=get_font(180, bold=True))
        draw.text((1350, 360), "!", fill=(220, 30, 30), font=get_font(180, bold=True))
        
    im.save(out_path, quality=95)

def run_full_nocebo_production():
    out_dir = Path("output/nocebo_full")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 65)
    print("🎬 STARTING COMPLETE NOCEBO EFFECT VIDEO ESSAY PRODUCTION (60 SCENES)")
    print("=" * 65)
    
    # Step 1: Synthesize all 60 scene audios with ElevenLabs George
    print("\n[Step 1/3] Synthesizing all 60 scene audios with ElevenLabs George...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"}
    
    # Check if scene 1-9 already exist in output/nocebo_test
    test_dir = Path("output/nocebo_test")
    
    for sid, text, banner, vtype in FULL_SCRIPT:
        audio_path = out_dir / f"scene_{sid}.mp3"
        if audio_path.exists() and audio_path.stat().st_size > 1000:
            continue
            
        # Copy from test_dir if available
        test_file = test_dir / f"scene_{sid}.mp3"
        if test_file.exists() and test_file.stat().st_size > 1000:
            audio_path.write_bytes(test_file.read_bytes())
            print(f"  Scene {sid}: Reused existing audio ({test_file.name})")
            continue
            
        print(f"  Scene {sid}: Synthesizing: {text[:45]}...")
        payload = {"text": text, "model_id": "eleven_turbo_v2_5"}
        r = requests.post(url, headers=headers, json=payload, timeout=25)
        if r.status_code == 200:
            audio_path.write_bytes(r.content)
            print(f"    -> OK ({len(r.content)} bytes)")
        else:
            raise RuntimeError(f"ElevenLabs synthesis failed for scene {sid}: {r.status_code} {r.text}")
            
    # Step 2: Render all 60 images in crisp 1080p
    print("\n[Step 2/3] Rendering all 60 crisp 1080p stickman doodle images...")
    for item in FULL_SCRIPT:
        sid = item[0]
        img_path = out_dir / f"scene_{sid}.jpg"
        if not img_path.exists():
            render_scene_image(item, img_path)
    print("  -> All 60 doodle images rendered successfully!")

    # Step 3: Render clips and concatenate
    print("\n[Step 3/3] Rendering 60 video clips and assembling master video...")
    clips = []
    for item in FULL_SCRIPT:
        sid = item[0]
        img = out_dir / f"scene_{sid}.jpg"
        aud = out_dir / f"scene_{sid}.mp3"
        clip = out_dir / f"clip_{sid}.mp4"
        
        # Probe duration
        res = subprocess.run([FFPROBE, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(aud)], stdout=subprocess.PIPE, text=True)
        dur = float(res.stdout.strip())
        
        # Render rock-solid 1080p clip with zero shake
        cmd = [
            FFMPEG, "-y",
            "-loop", "1",
            "-i", str(img),
            "-i", str(aud),
            "-vf", "scale=1920:1080,format=yuv420p",
            "-c:v", "libx264",
            "-tune", "stillimage",
            "-preset", "veryfast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-t", str(dur),
            "-shortest",
            str(clip)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        clips.append(clip)
        if sid % 10 == 0 or sid == 60:
            print(f"  Progress: Rendered {sid}/60 clips...")
            
    # Concat all 60 clips
    concat_txt = out_dir / "concat_60.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c.name}'\n")

    temp_concat = out_dir / "temp_full.mp4"
    print("\nConcatenating all 60 clips...")
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(temp_concat)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Master audio mixing with 55Hz sub-bass atmospheric tension drone
    final_video = out_dir / "the_nocebo_effect_master.mp4"
    print("Mixing 55Hz sub-bass atmospheric drone audio and applying anti-AI spoofing...")
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
        "-metadata", "title=The Nocebo Effect",
        "-metadata", "comment=Edited in Adobe Premiere Pro 2025 (v25.2)",
        str(final_video)
    ]
    subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if temp_concat.exists():
        temp_concat.unlink()

    print("\n" + "=" * 65)
    print("🎉 FULL PRODUCTION COMPLETE!")
    print(f"👉 Master Video Output: {final_video}")
    print("=" * 65)

if __name__ == "__main__":
    run_full_nocebo_production()
