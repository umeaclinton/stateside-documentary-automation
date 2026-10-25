import math
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = True):
    font_candidates = [
        # Linux standard paths
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        # Windows standard paths
        f"C:/Windows/Fonts/{'arialbd.ttf' if bold else 'arial.ttf'}",
        f"C:/Windows/Fonts/{'comicbd.ttf' if bold else 'comic.ttf'}",
        f"C:/Windows/Fonts/{'calibrib.ttf' if bold else 'calibri.ttf'}",
        f"C:/Windows/Fonts/{'segoeuib.ttf' if bold else 'segoeui.ttf'}",
        # Fallback names
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arial.ttf"
    ]
    for fn in font_candidates:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def draw_wobbly_line(draw: ImageDraw.ImageDraw, points: List[Tuple[float, float]], fill="black", width=6, roughness=2.2):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(int(dist / 14), 1)
        prev_pt = (x1, y1)
        for s in range(1, steps + 1):
            t = s / steps
            mid_x = x1 + (x2 - x1) * t + random.uniform(-roughness, roughness)
            mid_y = y1 + (y2 - y1) * t + random.uniform(-roughness, roughness)
            if s == steps:
                mid_x, mid_y = x2, y2
            draw.line([prev_pt, (mid_x, mid_y)], fill=fill, width=width)
            prev_pt = (mid_x, mid_y)

def draw_circle_wobbly(draw: ImageDraw.ImageDraw, cx: float, cy: float, r: float, fill=None, outline="black", width=6):
    num_pts = 28
    pts = []
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        cur_r = r + random.uniform(-2.5, 2.5)
        pts.append((cx + cur_r * math.cos(angle), cy + cur_r * math.sin(angle)))
    pts.append(pts[0])
    if fill:
        draw.polygon(pts, fill=fill)
    draw_wobbly_line(draw, pts, fill=outline, width=width)

def draw_stickman(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, mood: str = "normal", fill: str = "white"):
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
        # Sweat drops
        draw.arc([cx + int(50 * scale), cy - int(110 * scale), cx + int(70 * scale), cy - int(80 * scale)], 40, 260, fill=(30, 140, 220), width=4)
    elif mood == "thinking":
        draw.line([(cx - int(15 * scale), cy - int(60 * scale)), (cx + int(15 * scale), cy - int(60 * scale))], fill="black", width=5)
        draw.arc([cx + int(35 * scale), cy - int(115 * scale), cx + int(85 * scale), cy - int(75 * scale)], 0, 360, fill=(240, 200, 30), width=5)
    elif mood == "shocked":
        draw.ellipse([cx - int(18 * scale), cy - int(70 * scale), cx + int(18 * scale), cy - int(40 * scale)], fill="black")
        draw.line([(cx - int(35 * scale), cy - int(120 * scale)), (cx - int(15 * scale), cy - int(105 * scale))], fill="black", width=5)
        draw.line([(cx + int(35 * scale), cy - int(120 * scale)), (cx + int(15 * scale), cy - int(105 * scale))], fill="black", width=5)
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
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(110 * scale), sh_y - int(70 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(110 * scale), sh_y - int(70 * scale))], width=7)
    elif mood == "scared":
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(70 * scale), sh_y + int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(70 * scale), sh_y + int(80 * scale))], width=7)
    elif mood == "pointing":
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(60 * scale), sh_y + int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(130 * scale), sh_y - int(30 * scale))], width=7)
    elif mood == "shocked":
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(90 * scale), sh_y - int(60 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(90 * scale), sh_y - int(60 * scale))], width=7)
    else:
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(80 * scale), sh_y + int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(80 * scale), sh_y + int(80 * scale))], width=7)

# -----------------------------------------------------------------------------
# Rich Semantic Illustrated Primitives
# -----------------------------------------------------------------------------

def draw_hospital_bed_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Hospital Bed Frame
    bed_y = cy + 120
    draw.rectangle([cx - 320, bed_y - 40, cx + 220, bed_y + 10], fill=(235, 238, 245), outline="black", width=6)
    # Bed legs
    draw_wobbly_line(draw, [(cx - 300, bed_y + 10), (cx - 300, bed_y + 140)], width=7)
    draw_wobbly_line(draw, [(cx + 200, bed_y + 10), (cx + 200, bed_y + 140)], width=7)
    # Headboard
    draw_wobbly_line(draw, [(cx - 320, bed_y - 120), (cx - 320, bed_y + 140)], width=8)
    
    # Patient stickman lying down
    head_x = cx - 220
    head_y = bed_y - 70
    draw_circle_wobbly(draw, head_x, head_y, 45, fill="white", width=5)
    # Closed eyes (pain)
    draw_wobbly_line(draw, [(head_x - 20, head_y - 5), (head_x - 5, head_y + 2)], width=4)
    draw_wobbly_line(draw, [(head_x + 5, head_y - 5), (head_x + 20, head_y + 2)], width=4)
    # Blanket
    draw.rectangle([cx - 160, bed_y - 30, cx + 210, bed_y + 10], fill=(180, 215, 245), outline="black", width=5)
    # Sweat droplets
    for dx in [20, 45]:
        draw.arc([head_x + dx, head_y - 40, head_x + dx + 15, head_y - 15], 30, 270, fill=(30, 140, 220), width=4)
        
    # IV Stand on right
    iv_x = cx + 320
    draw_wobbly_line(draw, [(iv_x, cy - 220), (iv_x, cy + 260)], width=6)
    draw_wobbly_line(draw, [(iv_x - 50, cy + 260), (iv_x + 50, cy + 260)], width=6)
    # IV Bag
    draw.rectangle([iv_x - 30, cy - 180, iv_x + 30, cy - 80], fill=(240, 248, 255), outline="black", width=4)
    draw.rectangle([iv_x - 25, cy - 140, iv_x + 25, cy - 85], fill=(190, 225, 255), outline=None)
    # Tube to patient
    draw_wobbly_line(draw, [(iv_x, cy - 80), (cx - 50, bed_y - 20)], fill=(70, 130, 180), width=3)


def draw_ecg_monitor_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, bpm_text: str = "148 BPM", scale: float = 1.0):
    # Monitor Body
    mw, mh = 620, 400
    draw.rectangle([cx - mw//2, cy - mh//2, cx + mw//2, cy + mh//2], fill=(20, 25, 30), outline="black", width=8)
    draw.rectangle([cx - mw//2 + 20, cy - mh//2 + 20, cx + mw//2 - 20, cy + mh//2 - 20], fill=(12, 16, 20), outline=(50, 60, 70), width=4)
    
    # Green ECG Zigzag line
    ecg_y = cy + 40
    ecg_pts = [
        (cx - 260, ecg_y),
        (cx - 180, ecg_y),
        (cx - 150, ecg_y - 25),
        (cx - 130, ecg_y + 35),
        (cx - 110, ecg_y - 120),  # Peak QRS
        (cx - 90,  ecg_y + 80),
        (cx - 70,  ecg_y),
        (cx - 10,  ecg_y),
        (cx + 20,  ecg_y - 25),
        (cx + 40,  ecg_y + 35),
        (cx + 60,  ecg_y - 130),  # Peak QRS 2
        (cx + 80,  ecg_y + 90),
        (cx + 100, ecg_y),
        (cx + 260, ecg_y),
    ]
    for i in range(len(ecg_pts) - 1):
        draw.line([ecg_pts[i], ecg_pts[i+1]], fill=(30, 220, 90), width=6)
        
    # BPM text in electric yellow/red
    f_bpm = get_font(68, bold=True)
    draw.text((cx - 250, cy - 150), bpm_text, fill=(255, 60, 50), font=f_bpm)
    draw.text((cx + 80, cy - 145), "CRITICAL", fill=(255, 230, 20), font=get_font(42, bold=True))
    draw.text((cx - 250, cy + 110), "BP: 80 / 40 mmHg", fill=(180, 200, 220), font=get_font(38, bold=True))


def draw_pill_bottle_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Prescription bottle on side
    bx, by = cx - 220, cy + 40
    # Bottle cylinder
    draw.rectangle([bx - 140, by - 60, bx + 40, by + 60], fill=(235, 140, 30), outline="black", width=6)
    # White label
    draw.rectangle([bx - 100, by - 45, bx + 10, by + 45], fill="white", outline="black", width=3)
    draw_wobbly_line(draw, [(bx - 90, by - 20), (bx, by - 20)], fill="black", width=3)
    draw_wobbly_line(draw, [(bx - 90, by + 5), (bx, by + 5)], fill="black", width=3)
    # White cap off to side
    draw.rectangle([bx + 40, by - 50, bx + 65, by + 50], fill=(245, 245, 245), outline="black", width=5)
    
    # Spilled capsules (half colored, half white)
    capsule_positions = [
        (cx - 80, cy + 60, 25),
        (cx - 20, cy + 110, -40),
        (cx + 40, cy + 30, 60),
        (cx + 90, cy + 90, -15),
        (cx + 150, cy + 50, 45),
        (cx + 210, cy + 110, -30),
        (cx + 270, cy + 40, 10),
    ]
    for px, py, rot in capsule_positions:
        # Capsule body
        draw.ellipse([px - 35, py - 18, px + 35, py + 18], fill="white", outline="black", width=4)
        # Left half red
        draw.chord([px - 35, py - 18, px + 35, py + 18], 90, 270, fill=(220, 40, 40), outline="black", width=3)
        
    # Giant Callout badge: "29 PILLS"
    draw.rectangle([cx + 60, cy - 160, cx + 380, cy - 70], fill=(255, 230, 0), outline="black", width=6)
    draw.text((cx + 90, cy - 150), "29 EMPTY PILLS", fill="black", font=get_font(42, bold=True))


def draw_doctor_patient_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Doctor on Left
    doc_x = cx - 260
    draw_stickman(draw, doc_x, cy, scale=1.05, mood="normal")
    # Stethoscope
    draw.arc([doc_x - 30, cy + 10, doc_x + 30, cy + 70], 0, 180, fill=(70, 70, 70), width=5)
    draw.ellipse([doc_x + 22, cy + 65, doc_x + 38, cy + 81], fill="black")
    # Head mirror / light
    draw.ellipse([doc_x + 25, cy - 110, doc_x + 45, cy - 90], fill=(200, 220, 255), outline="black", width=3)
    
    # Patient on Right
    pat_x = cx + 220
    draw_stickman(draw, pat_x, cy, scale=0.95, mood="scared")
    
    # Speech bubble from Doctor to Patient
    draw.rectangle([cx - 100, cy - 180, cx + 120, cy - 80], fill=(255, 255, 240), outline="black", width=5)
    draw.polygon([(cx - 40, cy - 80), (cx - 80, cy - 40), (cx - 10, cy - 80)], fill=(255, 255, 240))
    draw_wobbly_line(draw, [(cx - 40, cy - 80), (cx - 80, cy - 40)], width=5)
    draw_wobbly_line(draw, [(cx - 80, cy - 40), (cx - 10, cy - 80)], width=5)
    draw.text((cx - 80, cy - 155), "THE TRUTH", fill=(220, 30, 30), font=get_font(42, bold=True))


def draw_anatomical_heart_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Heart shape
    hr = 130
    draw.polygon([
        (cx, cy + hr),
        (cx - hr, cy - int(hr * 0.2)),
        (cx - int(hr * 0.7), cy - hr),
        (cx, cy - int(hr * 0.4)),
        (cx + int(hr * 0.7), cy - hr),
        (cx + hr, cy - int(hr * 0.2)),
    ], fill=(225, 30, 30))
    draw_wobbly_line(draw, [
        (cx, cy + hr),
        (cx - hr, cy - int(hr * 0.2)),
        (cx - int(hr * 0.7), cy - hr),
        (cx, cy - int(hr * 0.4)),
        (cx + int(hr * 0.7), cy - hr),
        (cx + hr, cy - int(hr * 0.2)),
        (cx, cy + hr)
    ], width=7)
    
    # Pulse shockwave ripples
    for r_offset in [50, 110, 170]:
        draw.arc([cx - hr - r_offset, cy - hr - r_offset, cx + hr + r_offset, cy + hr + r_offset], 20, 160, fill=(240, 180, 20), width=5)
        draw.arc([cx - hr - r_offset, cy - hr - r_offset, cx + hr + r_offset, cy + hr + r_offset], 200, 340, fill=(240, 180, 20), width=5)
        
    # Sound FX text
    draw.text((cx - 360, cy - 60), "THUMP", fill="black", font=get_font(60, bold=True))
    draw.text((cx + 220, cy + 20), "THUMP", fill="black", font=get_font(60, bold=True))


def draw_clock_wall_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, time_label: str = "2:00 AM", scale: float = 1.0):
    # Big Clock face
    r = 160
    draw_circle_wobbly(draw, cx, cy - 20, r, fill=(250, 250, 252), width=7)
    # Clock hour ticks
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        x1 = cx + (r - 25) * math.cos(rad)
        y1 = cy - 20 + (r - 25) * math.sin(rad)
        x2 = cx + (r - 8) * math.cos(rad)
        y2 = cy - 20 + (r - 8) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill="black", width=4)
        
    # Hands (pointing at 2:00)
    # Center dot
    draw.ellipse([cx - 8, cy - 28, cx + 8, cy - 12], fill="black")
    # Hour hand to 2 o'clock
    draw_wobbly_line(draw, [(cx, cy - 20), (cx + 65, cy - 65)], width=8)
    # Minute hand to 12 o'clock
    draw_wobbly_line(draw, [(cx, cy - 20), (cx, cy - 135)], width=6)
    
    # Text badge
    draw.rectangle([cx - 160, cy + 180, cx + 160, cy + 260], fill=(255, 230, 0), outline="black", width=6)
    draw.text((cx - 120, cy + 190), time_label, fill="black", font=get_font(55, bold=True))


def draw_lab_microscope_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Microscope
    mx = cx - 180
    my = cy + 40
    # Base
    draw.rectangle([mx - 100, my + 100, mx + 100, my + 130], fill=(160, 170, 180), outline="black", width=6)
    # Arm
    draw_wobbly_line(draw, [(mx + 50, my + 100), (mx + 80, my - 60), (mx, my - 120)], width=10)
    # Eyepiece
    draw_wobbly_line(draw, [(mx - 50, my - 160), (mx + 20, my - 90)], width=14)
    # Stage & clips
    draw.rectangle([mx - 80, my + 10, mx + 40, my + 25], fill="black")
    
    # Laboratory Flasks on Right
    fx = cx + 180
    fy = cy + 80
    # Erlenmeyer Flask
    draw.polygon([(fx - 70, fy + 80), (fx + 70, fy + 80), (fx + 20, fy - 50), (fx - 20, fy - 50)], fill=(245, 250, 255))
    draw_wobbly_line(draw, [(fx - 70, fy + 80), (fx + 70, fy + 80), (fx + 20, fy - 50), (fx - 20, fy - 50), (fx - 70, fy + 80)], width=6)
    # Purple/Cyan chemical liquid inside
    draw.polygon([(fx - 60, fy + 75), (fx + 60, fy + 75), (fx + 35, fy + 20), (fx - 35, fy + 20)], fill=(160, 70, 220))
    # Bubbles
    draw_circle_wobbly(draw, fx - 10, fy - 10, 12, fill="white", width=3)
    draw_circle_wobbly(draw, fx + 15, fy - 70, 18, fill="white", width=3)


def draw_eureka_moment_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Stickman looking up happily
    draw_stickman(draw, cx, cy + 60, scale=1.05, mood="happy")
    
    # Glowing Lightbulb overhead
    bx = cx
    by = cy - 200
    # Bulb glass
    draw_circle_wobbly(draw, bx, by, 50, fill=(255, 240, 60), width=6)
    # Base screw
    draw.rectangle([bx - 18, by + 45, bx + 18, by + 75], fill=(180, 180, 180), outline="black", width=4)
    # Radiating light rays
    for angle_deg in range(0, 360, 40):
        rad = math.radians(angle_deg)
        x1 = bx + 70 * math.cos(rad)
        y1 = by + 70 * math.sin(rad)
        x2 = bx + 115 * math.cos(rad)
        y2 = by + 115 * math.sin(rad)
        draw_wobbly_line(draw, [(x1, y1), (x2, y2)], fill=(245, 190, 20), width=6)


def draw_argument_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Left stickman leaning right angrily
    draw_stickman(draw, cx - 220, cy, scale=0.95, mood="pointing")
    # Right stickman leaning left angrily
    draw_stickman(draw, cx + 220, cy, scale=0.95, mood="pointing")
    
    # Comic book spiky anger bubble in center
    draw.polygon([
        (cx - 100, cy - 80), (cx - 40, cy - 140), (cx + 20, cy - 100),
        (cx + 90, cy - 150), (cx + 60, cy - 70), (cx + 120, cy - 20),
        (cx + 50, cy + 20), (cx + 70, cy + 80), (cx, cy + 40),
        (cx - 60, cy + 90), (cx - 40, cy + 10), (cx - 110, cy - 10),
    ], fill=(255, 235, 235))
    draw_wobbly_line(draw, [
        (cx - 100, cy - 80), (cx - 40, cy - 140), (cx + 20, cy - 100),
        (cx + 90, cy - 150), (cx + 60, cy - 70), (cx + 120, cy - 20),
        (cx + 50, cy + 20), (cx + 70, cy + 80), (cx, cy + 40),
        (cx - 60, cy + 90), (cx - 40, cy + 10), (cx - 110, cy - 10),
        (cx - 100, cy - 80)
    ], width=6)
    draw.text((cx - 50, cy - 40), "! ! !", fill=(220, 30, 30), font=get_font(60, bold=True))


def draw_mirror_reflection_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    # Standing mirror frame
    mx = cx + 80
    draw.ellipse([mx - 140, cy - 240, mx + 140, cy + 220], fill=(240, 245, 255), outline="black", width=8)
    draw_wobbly_line(draw, [(mx - 140, cy + 220), (mx - 170, cy + 320)], width=8)
    draw_wobbly_line(draw, [(mx + 140, cy + 220), (mx + 170, cy + 320)], width=8)
    
    # Real Stickman on left looking into mirror
    draw_stickman(draw, cx - 260, cy + 30, scale=0.95, mood="thinking")
    
    # Reflected Stickman inside mirror (slightly different / question mark)
    draw_stickman(draw, mx, cy + 40, scale=0.85, mood="shocked")
    draw.text((mx + 45, cy - 120), "?", fill=(220, 30, 30), font=get_font(70, bold=True))


def draw_split_comparison_scene(draw: ImageDraw.ImageDraw, cx: float, cy: float, label_left: str, label_right: str, scale: float = 1.0):
    # Vertical dividing line down center
    draw_wobbly_line(draw, [(cx, cy - 280), (cx, cy + 280)], fill=(70, 70, 70), width=6)
    
    # Left Side: Danger / Negative (Red tone)
    draw.rectangle([cx - 480, cy - 240, cx - 80, cy - 160], fill=(255, 230, 230), outline=(220, 30, 30), width=5)
    draw.text((cx - 440, cy - 225), label_left, fill=(220, 30, 30), font=get_font(42, bold=True))
    draw_stickman(draw, cx - 280, cy + 60, scale=0.9, mood="sad")
    
    # Right Side: Recovery / Positive (Green tone)
    draw.rectangle([cx + 80, cy - 240, cx + 480, cy - 160], fill=(230, 255, 235), outline=(35, 145, 60), width=5)
    draw.text((cx + 120, cy - 225), label_right, fill=(35, 145, 60), font=get_font(42, bold=True))
    draw_stickman(draw, cx + 280, cy + 60, scale=0.9, mood="happy")


def draw_elephant_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, is_large: bool = False):
    body_w = int(280 * scale)
    body_h = int(180 * scale)
    color = (190, 195, 205) if is_large else (215, 220, 228)
    draw.ellipse([cx - body_w//2, cy - body_h//2, cx + body_w//2, cy + body_h//2], fill=color, outline="black", width=6)
    head_cx = cx + int(120 * scale)
    head_cy = cy - int(30 * scale)
    draw_circle_wobbly(draw, head_cx, head_cy, int(65 * scale), fill=color, width=6)
    draw.arc([head_cx - int(75 * scale), head_cy - int(65 * scale), head_cx + int(15 * scale), head_cy + int(45 * scale)], 80, 280, fill="black", width=6)
    draw.ellipse([head_cx + int(15 * scale), head_cy - int(10 * scale), head_cx + int(25 * scale), head_cy], fill="black")
    trunk_pts = [
        (head_cx + int(45 * scale), head_cy + int(15 * scale)),
        (head_cx + int(75 * scale), head_cy + int(80 * scale)),
        (head_cx + int(60 * scale), head_cy + int(130 * scale)),
        (head_cx + int(90 * scale), head_cy + int(140 * scale))
    ]
    draw_wobbly_line(draw, trunk_pts, width=8)
    if is_large:
        tusk_pts = [
            (head_cx + int(35 * scale), head_cy + int(35 * scale)),
            (head_cx + int(85 * scale), head_cy + int(55 * scale)),
            (head_cx + int(115 * scale), head_cy + int(45 * scale))
        ]
        draw_wobbly_line(draw, tusk_pts, fill=(245, 240, 210), width=8)
    for lx in [cx - int(90 * scale), cx - int(30 * scale), cx + int(40 * scale), cx + int(90 * scale)]:
        draw_wobbly_line(draw, [(lx, cy + int(70 * scale)), (lx, cy + int(170 * scale))], width=8)


def draw_rhino_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, is_fallen: bool = False):
    if is_fallen:
        draw.ellipse([cx - 180, cy + 20, cx + 180, cy + 130], fill=(225, 220, 215), outline="black", width=6)
        draw_wobbly_line(draw, [(cx + 170, cy + 80), (cx + 250, cy + 40)], width=7)
        draw_wobbly_line(draw, [(cx + 250, cy + 40), (cx + 280, cy + 90)], width=7)
        draw.line([(cx + 130, cy + 50), (cx + 150, cy + 70)], fill="black", width=5)
        draw.line([(cx + 150, cy + 50), (cx + 130, cy + 70)], fill="black", width=5)
        draw.text((cx - 80, cy - 60), "NO PREDATOR", fill=(220, 30, 30), font=get_font(45, bold=True))
    else:
        draw.ellipse([cx - 150, cy - 60, cx + 150, cy + 70], fill=(215, 215, 215), outline="black", width=6)
        draw_wobbly_line(draw, [(cx + 130, cy - 20), (cx + 190, cy - 80), (cx + 170, cy + 10)], width=7)
        for lx in [cx - 100, cx - 40, cx + 40, cx + 100]:
            draw_wobbly_line(draw, [(lx, cy + 50), (lx, cy + 140)], width=8)


def draw_brain_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    r = int(140 * scale)
    draw_circle_wobbly(draw, cx - int(60*scale), cy, r, fill=(255, 240, 245), width=6)
    draw_circle_wobbly(draw, cx + int(60*scale), cy, r, fill=(255, 240, 245), width=6)
    for i in range(5):
        sy = cy - int(80*scale) + i * int(35*scale)
        draw.arc([cx - int(100*scale), sy, cx + int(100*scale), sy + int(40*scale)], 20, 160, fill="black", width=5)
    draw.polygon([(cx - 20, cy - int(170*scale)), (cx + 10, cy - int(140*scale)), (cx - 10, cy - int(140*scale)), (cx + 20, cy - int(110*scale))], fill=(255, 200, 30))


def draw_bar_comparison(draw: ImageDraw.ImageDraw, cx: float, cy: float, label_a: str, val_a: int, label_b: str, val_b: int):
    draw_wobbly_line(draw, [(cx - 300, cy + 180), (cx + 300, cy + 180)], width=6)
    draw_wobbly_line(draw, [(cx - 300, cy + 180), (cx - 300, cy - 180)], width=6)
    h_a = int(val_a * 3.2)
    draw.rectangle([cx - 200, cy + 180 - h_a, cx - 70, cy + 180], fill=(40, 150, 60), outline="black", width=5)
    draw.text((cx - 180, cy + 180 - h_a - 65), f"{val_a}%", fill=(40, 150, 60), font=get_font(55, bold=True))
    draw.text((cx - 210, cy + 200), label_a, fill="black", font=get_font(42, bold=True))
    h_b = int(val_b * 3.2)
    draw.rectangle([cx + 70, cy + 180 - h_b, cx + 200, cy + 180], fill=(220, 40, 40), outline="black", width=5)
    draw.text((cx + 90, cy + 180 - h_b - 65), f"{val_b}%", fill=(220, 40, 40), font=get_font(55, bold=True))
    draw.text((cx + 60, cy + 200), label_b, fill="black", font=get_font(42, bold=True))


# -----------------------------------------------------------------------------
# Master Visual Frame Orchestrator
# -----------------------------------------------------------------------------

def render_masterpiece_frame(scene: Dict[str, Any], out_path: Path):
    sid = scene.get("scene_id", 1)
    narration = scene.get("narration", "")
    banner = scene.get("banner_text", "").upper()
    desc = scene.get("visual_description", "").lower()
    full_text = f"{narration.lower()} {desc.lower()} {banner.lower()}"
    
    random.seed(3000 + sid)
    im = Image.new("RGB", (1920, 1080), "white")
    draw = ImageDraw.Draw(im)
    
    # Ground horizon line
    draw_wobbly_line(draw, [(80, 950), (1840, 950)], width=6)
    
    # Banner formatting
    f_title = get_font(105, bold=True)
    f_sub = get_font(55, bold=False)
    
    is_danger = any(w in banner for w in ["BERSERK", "DEAD", "EXECUTION", "ATTACK", "CRISIS", "WARNING", "PARADOX", "KILL", "DANGER", "OVERDOSE", "SHUTDOWN"])
    is_success = any(w in banner for w in ["RESOLVED", "MENTOR", "SAVED", "NORMAL", "CALM", "PEACE", "FOUND", "RECOVERY", "CURE"])
    banner_color = (220, 30, 30) if is_danger else (35, 145, 60) if is_success else "black"
    
    lines = banner.split("\n")
    draw.text((180, 110), lines[0], fill=banner_color, font=f_title)
    if len(lines) > 1:
        draw.text((190, 230), lines[1], fill=(90, 90, 90), font=f_sub)
        
    cx, cy = 960, 580
    
    # -------------------------------------------------------------------------
    # Semantic Scene Matching (20+ Distinct Contextual Compositions)
    # -------------------------------------------------------------------------
    if any(k in full_text for k in ["hospital", "gown", "er bay", "bay", "paramedic", "bed", "patient", "ambulance", "intravenous", "iv bag"]):
        draw_hospital_bed_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["bpm", "blood pressure", "heartbeat", "ecg", "pulse", "monitor", "148 bpm", "vital"]):
        draw_ecg_monitor_scene(draw, cx, cy, bpm_text=banner if "BPM" in banner else "148 BPM")
        
    elif any(k in full_text for k in ["pill", "capsule", "overdose", "swallow", "antidepressant", "medication", "dose", "tablet"]):
        draw_pill_bottle_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["doctor", "physician", "nurse", "white coat", "stethoscope", "clinical"]):
        draw_doctor_patient_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["heart hammered", "racing heart", "cardiac", "chest", "organ"]):
        draw_anatomical_heart_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["clock", "2:00 am", "night", "hour", "hours later", "15 min", "minutes", "seconds", "morning"]):
        time_tag = "2:00 AM" if "2" in full_text else "15 MIN LATER" if "15" in full_text else "TIME PASSED"
        draw_clock_wall_scene(draw, cx, cy, time_label=time_tag)
        
    elif any(k in full_text for k in ["microscope", "laboratory", "flask", "chemical", "molecules", "biology", "dna"]):
        draw_lab_microscope_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["eureka", "truth", "discovered", "realized", "empty", "instant cure", "revelation"]):
        draw_eureka_moment_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["argument", "fight", "yell", "shout", "anger", "conflict"]):
        draw_argument_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["mirror", "reflection", "stranger", "voice confrontation", "self-image", "identity"]):
        draw_mirror_reflection_scene(draw, cx, cy)
        
    elif any(k in full_text for k in ["versus", "vs", "split", "contrast", "placebo vs nocebo", "expectation vs"]):
        draw_split_comparison_scene(draw, cx, cy, "NOCEBO (HARM)", "PLACEBO (HEAL)")
        
    elif any(k in full_text for k in ["rhino", "horn"]):
        is_dead = any(k in full_text for k in ["pinned", "broken", "dead", "execution", "shattered", "lies still"])
        draw_rhino_doodle(draw, cx, cy + 100, scale=1.2, is_fallen=is_dead)
        if not is_dead:
            draw_stickman(draw, 450, cy + 60, scale=0.9, mood="scared")
            
    elif any(k in full_text for k in ["elephant", "juvenile", "bull", "orphan"]):
        if any(k in full_text for k in ["mentor", "adult", "mature", "introduced"]):
            draw_elephant_doodle(draw, cx + 190, cy + 20, scale=1.4, is_large=True)
            draw_elephant_doodle(draw, cx - 380, cy + 140, scale=0.8, is_large=False)
            draw.text((cx + 90, cy - 230), "ADULT BULL (MENTOR)", fill=(40, 140, 60), font=get_font(50, bold=True))
        else:
            draw_elephant_doodle(draw, cx, cy + 90, scale=1.0, is_large=False)
            
    elif any(k in full_text for k in ["brain", "neurons", "psychology", "mental", "cognitive", "synapse"]):
        draw_brain_doodle(draw, cx, cy, scale=1.3)
        draw_stickman(draw, 420, cy + 60, scale=0.9, mood="thinking")
        
    elif any(k in full_text for k in ["percent", "statistic", "study", "italy", "clinical trial", "rate"]):
        draw_bar_comparison(draw, cx, cy, "INFORMED", 43, "UNINFORMED", 15)
        
    elif any(k in full_text for k in ["crowd", "social", "people", "bystander", "bystanders", "society"]):
        for idx, pos_x in enumerate([480, 720, 960, 1200, 1440]):
            draw_stickman(draw, pos_x, cy + 40, scale=0.85, mood="normal")
            
    elif any(k in full_text for k in ["panic", "despair", "headache", "terror", "agony"]):
        draw_stickman(draw, cx, cy + 60, scale=1.1, mood="shocked")
        draw.arc([cx - 100, cy - 140, cx + 100, cy - 20], 0, 360, fill=(220, 30, 30), width=6)
        
    elif any(k in full_text for k in ["why", "question", "paradox", "mystery"]):
        draw_stickman(draw, cx - 180, cy + 60, scale=1.0, mood="thinking")
        draw.arc([cx + 120, cy - 180, cx + 320, cy + 20], 180, 360, fill=(220, 40, 40), width=9)
        draw_wobbly_line(draw, [(cx + 320, cy - 80), (cx + 220, cy + 60)], fill=(220, 40, 40), width=9)
        draw.ellipse([cx + 205, cy + 120, cx + 235, cy + 150], fill=(220, 40, 40))
        
    else:
        # Dynamic Varied Composition Fallbacks (NEVER repeats identical layout)
        variant = sid % 4
        if variant == 0:
            # Stickman pointing at key banner stat
            draw_stickman(draw, cx - 240, cy + 60, scale=1.05, mood="pointing")
            draw_wobbly_line(draw, [(cx - 120, cy + 40), (cx + 260, cy + 40)], width=5)
            draw.rectangle([cx + 100, cy - 80, cx + 380, cy + 120], fill=(255, 250, 240), outline="black", width=5)
            draw.text((cx + 140, cy - 20), "OBSERVATION", fill="black", font=get_font(40, bold=True))
        elif variant == 1:
            # Walking along horizon into thought
            draw_stickman(draw, cx, cy + 60, scale=1.0, mood="thinking")
            draw.arc([cx + 250, cy - 180, cx + 450, cy + 20], 30, 280, fill=(240, 180, 40), width=6)
        elif variant == 2:
            # Dual stickmen discussing
            draw_stickman(draw, cx - 200, cy + 60, scale=0.95, mood="normal")
            draw_stickman(draw, cx + 200, cy + 60, scale=0.95, mood="thinking")
            draw.arc([cx - 50, cy - 100, cx + 50, cy - 20], 0, 180, fill=(100, 100, 100), width=4)
        else:
            # Stickman seated observing
            draw_stickman(draw, cx, cy + 60, scale=1.05, mood="normal")
            
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=95)
