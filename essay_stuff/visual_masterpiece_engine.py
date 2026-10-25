import math
import random
from pathlib import Path
from typing import Dict, Any, List, Tuple
from PIL import Image, ImageDraw, ImageFont

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
    elif mood == "thinking":
        draw.line([(cx - int(15 * scale), cy - int(60 * scale)), (cx + int(15 * scale), cy - int(60 * scale))], fill="black", width=5)
        draw.arc([cx + int(35 * scale), cy - int(115 * scale), cx + int(85 * scale), cy - int(75 * scale)], 0, 360, fill=(240, 200, 30), width=5)
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
    else:
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(80 * scale), sh_y + int(80 * scale))], width=7)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(80 * scale), sh_y + int(80 * scale))], width=7)

def draw_elephant_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, is_large: bool = False):
    body_w = int(280 * scale)
    body_h = int(180 * scale)
    color = (190, 195, 205) if is_large else (215, 220, 228)
    
    # Body oval
    draw.ellipse([cx - body_w//2, cy - body_h//2, cx + body_w//2, cy + body_h//2], fill=color, outline="black", width=6)
    
    # Head & ear
    head_cx = cx + int(120 * scale)
    head_cy = cy - int(30 * scale)
    draw_circle_wobbly(draw, head_cx, head_cy, int(65 * scale), fill=color, width=6)
    draw.arc([head_cx - int(75 * scale), head_cy - int(65 * scale), head_cx + int(15 * scale), head_cy + int(45 * scale)], 80, 280, fill="black", width=6)
    
    # Eye
    draw.ellipse([head_cx + int(15 * scale), head_cy - int(10 * scale), head_cx + int(25 * scale), head_cy], fill="black")
    
    # Trunk
    trunk_pts = [
        (head_cx + int(45 * scale), head_cy + int(15 * scale)),
        (head_cx + int(75 * scale), head_cy + int(80 * scale)),
        (head_cx + int(60 * scale), head_cy + int(130 * scale)),
        (head_cx + int(90 * scale), head_cy + int(140 * scale))
    ]
    draw_wobbly_line(draw, trunk_pts, width=8)
    
    # Tusk if large
    if is_large:
        tusk_pts = [
            (head_cx + int(35 * scale), head_cy + int(35 * scale)),
            (head_cx + int(85 * scale), head_cy + int(55 * scale)),
            (head_cx + int(115 * scale), head_cy + int(45 * scale))
        ]
        draw_wobbly_line(draw, tusk_pts, fill=(245, 240, 210), width=8)
    
    # Legs
    for lx in [cx - int(90 * scale), cx - int(30 * scale), cx + int(40 * scale), cx + int(90 * scale)]:
        draw_wobbly_line(draw, [(lx, cy + int(70 * scale)), (lx, cy + int(170 * scale))], width=8)

def draw_rhino_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0, is_fallen: bool = False):
    if is_fallen:
        # Fallen / dead rhino
        draw.ellipse([cx - 180, cy + 20, cx + 180, cy + 130], fill=(225, 220, 215), outline="black", width=6)
        # Broken horn on the ground
        draw_wobbly_line(draw, [(cx + 170, cy + 80), (cx + 250, cy + 40)], width=7)
        draw_wobbly_line(draw, [(cx + 250, cy + 40), (cx + 280, cy + 90)], width=7)
        # Eye X
        draw.line([(cx + 130, cy + 50), (cx + 150, cy + 70)], fill="black", width=5)
        draw.line([(cx + 150, cy + 50), (cx + 130, cy + 70)], fill="black", width=5)
        draw.text((cx - 80, cy - 60), "NO PREDATOR", fill=(220, 30, 30), font=get_font(45, bold=True))
    else:
        # Standing rhino
        draw.ellipse([cx - 150, cy - 60, cx + 150, cy + 70], fill=(215, 215, 215), outline="black", width=6)
        draw_wobbly_line(draw, [(cx + 130, cy - 20), (cx + 190, cy - 80), (cx + 170, cy + 10)], width=7)
        for lx in [cx - 100, cx - 40, cx + 40, cx + 100]:
            draw_wobbly_line(draw, [(lx, cy + 50), (lx, cy + 140)], width=8)

def draw_brain_doodle(draw: ImageDraw.ImageDraw, cx: float, cy: float, scale: float = 1.0):
    r = int(140 * scale)
    draw_circle_wobbly(draw, cx - int(60*scale), cy, r, fill=(255, 240, 245), width=6)
    draw_circle_wobbly(draw, cx + int(60*scale), cy, r, fill=(255, 240, 245), width=6)
    # Inner sulci/folds
    for i in range(5):
        sy = cy - int(80*scale) + i * int(35*scale)
        draw.arc([cx - int(100*scale), sy, cx + int(100*scale), sy + int(40*scale)], 20, 160, fill="black", width=5)
    # Synapse spark
    draw.polygon([(cx - 20, cy - int(170*scale)), (cx + 10, cy - int(140*scale)), (cx - 10, cy - int(140*scale)), (cx + 20, cy - int(110*scale))], fill=(255, 200, 30))

def draw_bar_comparison(draw: ImageDraw.ImageDraw, cx: float, cy: float, label_a: str, val_a: int, label_b: str, val_b: int):
    # Axis
    draw_wobbly_line(draw, [(cx - 300, cy + 180), (cx + 300, cy + 180)], width=6)
    draw_wobbly_line(draw, [(cx - 300, cy + 180), (cx - 300, cy - 180)], width=6)
    
    # Bar A
    h_a = int(val_a * 3.2)
    draw.rectangle([cx - 200, cy + 180 - h_a, cx - 70, cy + 180], fill=(40, 150, 60), outline="black", width=5)
    draw.text((cx - 180, cy + 180 - h_a - 65), f"{val_a}%", fill=(40, 150, 60), font=get_font(55, bold=True))
    draw.text((cx - 210, cy + 200), label_a, fill="black", font=get_font(42, bold=True))
    
    # Bar B
    h_b = int(val_b * 3.2)
    draw.rectangle([cx + 70, cy + 180 - h_b, cx + 200, cy + 180], fill=(220, 40, 40), outline="black", width=5)
    draw.text((cx + 90, cy + 180 - h_b - 65), f"{val_b}%", fill=(220, 40, 40), font=get_font(55, bold=True))
    draw.text((cx + 60, cy + 200), label_b, fill="black", font=get_font(42, bold=True))

def render_masterpiece_frame(scene: Dict[str, Any], out_path: Path):
    sid = scene.get("scene_id", 1)
    narration = scene.get("narration", "")
    banner = scene.get("banner_text", "").upper()
    desc = scene.get("visual_description", "").lower()
    
    random.seed(3000 + sid)
    im = Image.new("RGB", (1920, 1080), "white")
    draw = ImageDraw.Draw(im)
    
    # Ground horizon line
    draw_wobbly_line(draw, [(80, 950), (1840, 950)], width=6)
    
    # Banner formatting
    f_title = get_font(105, bold=True)
    f_sub = get_font(55, bold=False)
    
    # Color coding banner
    is_danger = any(w in banner for w in ["BERSERK", "DEAD", "EXECUTION", "ATTACK", "CRISIS", "WARNING", "PARADOX", "KILL"])
    is_success = any(w in banner for w in ["RESOLVED", "MENTOR", "SAVED", "NORMAL", "CALM", "PEACE", "FOUND"])
    banner_color = (220, 30, 30) if is_danger else (35, 145, 60) if is_success else "black"
    
    # Draw Banner Text
    lines = banner.split("\n")
    draw.text((180, 110), lines[0], fill=banner_color, font=f_title)
    if len(lines) > 1:
        draw.text((190, 230), lines[1], fill=(90, 90, 90), font=f_sub)
        
    # Semantic Scene Composition based on description & narration
    n_lower = narration.lower()
    
    if any(k in desc or k in n_lower for k in ["rhino", "horn"]):
        is_dead = any(k in desc or k in n_lower for k in ["pinned", "broken", "dead", "execution", "shattered", "lies still"])
        draw_rhino_doodle(draw, 960, 680, scale=1.2, is_fallen=is_dead)
        if not is_dead:
            draw_stickman(draw, 450, 640, scale=0.9, mood="scared")
            
    elif any(k in desc or k in n_lower for k in ["elephant", "juvenile", "bull", "orphan"]):
        if any(k in desc or k in n_lower for k in ["mentor", "adult", "mature", "introduced"]):
            # Large adult mentor elephant with juvenile beside him
            draw_elephant_doodle(draw, 1150, 600, scale=1.4, is_large=True)
            draw_elephant_doodle(draw, 580, 720, scale=0.8, is_large=False)
            draw.text((1050, 350), "ADULT BULL (MENTOR)", fill=(40, 140, 60), font=get_font(50, bold=True))
        elif any(k in desc or k in n_lower for k in ["charging", "berserk", "violence", "execution", "attack"]):
            # Charging aggressive elephant
            draw_elephant_doodle(draw, 1000, 640, scale=1.3, is_large=False)
            # Action lines & dust cloud
            for dx in [350, 450, 550]:
                draw_circle_wobbly(draw, dx, 870, 45, fill=(245, 240, 230), outline="black", width=4)
            draw.text((950, 370), "! ! !", fill=(220, 30, 30), font=get_font(90, bold=True))
        else:
            # Lone orphan elephant
            draw_elephant_doodle(draw, 960, 670, scale=0.95, is_large=False)
            draw.arc([1300, 350, 1500, 550], 30, 300, fill=(240, 180, 40), width=6) # Sunset
            
    elif any(k in desc or k in n_lower for k in ["brain", "neurons", "psychology", "mental"]):
        draw_brain_doodle(draw, 960, 580, scale=1.3)
        draw_stickman(draw, 420, 640, scale=0.9, mood="thinking")
        draw_wobbly_line(draw, [(520, 560), (750, 560)], width=5)
        
    elif any(k in desc or k in n_lower for k in ["study", "nature", "science", "percent", "statistic", "rate", "vs"]):
        draw_bar_comparison(draw, 960, 560, "NO MENTORS", 85, "WITH BULLS", 0)
        
    elif any(k in desc or k in n_lower for k in ["crowd", "social", "people", "humans", "mirror"]):
        draw_stickman(draw, 600, 620, scale=0.85, mood="normal")
        draw_stickman(draw, 850, 590, scale=1.0, mood="normal")
        draw_stickman(draw, 1100, 610, scale=0.9, mood="normal")
        draw_stickman(draw, 1350, 630, scale=0.8, mood="normal")
        draw_wobbly_line(draw, [(550, 420), (1400, 420)], width=4)
        
    elif any(k in desc or k in n_lower for k in ["now you do", "curious", "smile", "conclusion", "sign"]):
        # Signature Zenn Punchline Sign-off
        draw_stickman(draw, 960, 560, scale=1.2, mood="happy")
        # Starburst / excitement
        for angle_deg in range(0, 360, 45):
            rad = math.radians(angle_deg)
            x1 = 960 + 260 * math.cos(rad)
            y1 = 450 + 260 * math.sin(rad)
            x2 = 960 + 330 * math.cos(rad)
            y2 = 450 + 330 * math.sin(rad)
            draw_wobbly_line(draw, [(x1, y1), (x2, y2)], fill=(240, 190, 40), width=6)
        draw.text((820, 830), "STAY CURIOUS.", fill="black", font=get_font(55, bold=True))
        
    elif any(k in desc or k in n_lower for k in ["why", "question", "paradox", "mystery"]):
        draw_stickman(draw, 720, 580, scale=1.1, mood="thinking")
        # Giant wobbly question mark
        draw.arc([1150, 360, 1380, 580], 180, 360, fill=(220, 40, 40), width=9)
        draw_wobbly_line(draw, [(1380, 470), (1260, 620)], fill=(220, 40, 40), width=9)
        draw.ellipse([1245, 680, 1275, 710], fill=(220, 40, 40))
        
    else:
        # Default smart layout: Storyteller stickman observing key event
        draw_stickman(draw, 580, 620, scale=1.0, mood="thinking")
        # Document / Clipboard with checkmarks
        draw.rectangle([1100, 360, 1450, 780], fill=(255, 252, 240), outline="black", width=6)
        for ly in range(430, 730, 60):
            draw_wobbly_line(draw, [(1150, ly), (1400, ly)], fill=(80, 80, 80), width=4)
        draw_wobbly_line(draw, [(700, 580), (1050, 580)], width=5)
        
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=95)
