import math
import random
from pathlib import Path
from typing import Dict, Any, Tuple
from PIL import Image, ImageDraw, ImageFont

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent

def get_thumbnail_font(size: int, font_name: str = "impact.ttf") -> ImageFont.ImageFont:
    paths = [
        Path(f"C:/Windows/Fonts/{font_name}"),
        Path(f"C:/Windows/Fonts/arialbd.ttf"),
        Path(f"C:/Windows/Fonts/comicbd.ttf")
    ]
    for p in paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_stroked_text(
    draw: ImageDraw.ImageDraw,
    pos: Tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill_color: str = "#FFE600", # Vivid yellow
    stroke_color: str = "#000000",
    stroke_width: int = 14
):
    """
    Renders massive high-contrast YouTube thumbnail text with a heavy black outline.
    """
    x, y = pos
    # Draw thick stroke around text
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    # Draw main fill text
    draw.text((x, y), text, font=font, fill=fill_color)

def draw_wobbly_line(draw: ImageDraw.ImageDraw, points, fill="black", width=7, roughness=2.5):
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

def draw_circle_wobbly(draw: ImageDraw.ImageDraw, cx, cy, r, fill=None, outline="black", width=7):
    num_pts = 32
    pts = []
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        cur_r = r + random.uniform(-3, 3)
        pts.append((cx + cur_r * math.cos(angle), cy + cur_r * math.sin(angle)))
    pts.append(pts[0])
    if fill:
        draw.polygon(pts, fill=fill)
    draw_wobbly_line(draw, pts, fill=outline, width=width)

def draw_thumbnail_stickman(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.3, expression: str = "sweat"):
    """
    Draws a large, expressive, iconic doodle stickman tailored for high YouTube thumbnail CTR.
    """
    head_r = int(95 * scale)
    head_cy = cy - int(120 * scale)
    
    # Glowing aura if peak/enlightened
    if expression == "glowing":
        for dr in [45, 30, 15]:
            draw.ellipse([cx - head_r - dr, head_cy - head_r - dr, cx + head_r + dr, head_cy + head_r + dr], fill=(255, 245, 140))
            
    # White head
    draw_circle_wobbly(draw, cx, head_cy, head_r, fill="#FFFFFF", width=8)
    
    # Eyes
    eye_r = int(12 * scale)
    ey = head_cy - int(15 * scale)
    draw.ellipse([cx - int(35 * scale) - eye_r, ey - eye_r, cx - int(35 * scale) + eye_r, ey + eye_r], fill="black")
    draw.ellipse([cx + int(35 * scale) - eye_r, ey - eye_r, cx + int(35 * scale) + eye_r, ey + eye_r], fill="black")
    
    # Eyebrows & Mouth
    if expression in ["sweat", "scared", "worried"]:
        # Worried slanted brows
        draw.line([(cx - int(50 * scale), ey - int(25 * scale)), (cx - int(20 * scale), ey - int(35 * scale))], fill="black", width=6)
        draw.line([(cx + int(50 * scale), ey - int(25 * scale)), (cx + int(20 * scale), ey - int(35 * scale))], fill="black", width=6)
        # Shivering open mouth
        draw.arc([cx - int(30 * scale), head_cy + int(10 * scale), cx + int(30 * scale), head_cy + int(55 * scale)], 180, 360, fill="black", width=7)
        # Giant blue sweat droplets
        for sx, sy in [(cx - int(80 * scale), head_cy - int(30 * scale)), (cx + int(85 * scale), head_cy - int(20 * scale))]:
            draw.ellipse([sx - 14, sy - 24, sx + 14, sy + 24], fill="#42A5F5", outline="black", width=4)
            
    elif expression == "questioning":
        # One raised brow
        draw.line([(cx - int(50 * scale), ey - int(40 * scale)), (cx - int(20 * scale), ey - int(30 * scale))], fill="black", width=6)
        draw.arc([cx + int(20 * scale), ey - int(45 * scale), cx + int(55 * scale), ey - int(25 * scale)], 180, 360, fill="black", width=6)
        # Crooked mouth
        draw.line([(cx - int(25 * scale), head_cy + int(35 * scale)), (cx + int(25 * scale), head_cy + int(25 * scale))], fill="black", width=7)
        
    else: # Calm / smiling
        draw.arc([cx - int(35 * scale), head_cy + int(10 * scale), cx + int(35 * scale), head_cy + int(50 * scale)], 0, 180, fill="black", width=7)
        
    # Spine
    spine_len = int(220 * scale)
    draw_wobbly_line(draw, [(cx, head_cy + head_r), (cx, head_cy + head_r + spine_len)], width=9)
    
    # Arms
    hip_y = head_cy + head_r + spine_len
    sh_y = head_cy + head_r + int(40 * scale)
    if expression in ["sweat", "scared"]:
        # Hands clutching head or cheeks
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(110 * scale), head_cy + int(10 * scale))], width=8)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(110 * scale), head_cy + int(10 * scale))], width=8)
    elif expression == "questioning":
        # One hand up scratching head, other out
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(120 * scale), head_cy - int(20 * scale))], width=8)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(130 * scale), sh_y + int(40 * scale))], width=8)
    else:
        draw_wobbly_line(draw, [(cx, sh_y), (cx - int(100 * scale), sh_y + int(120 * scale))], width=8)
        draw_wobbly_line(draw, [(cx, sh_y), (cx + int(100 * scale), sh_y + int(120 * scale))], width=8)
        
    # Legs
    leg_len = int(200 * scale)
    draw_wobbly_line(draw, [(cx, hip_y), (cx - int(80 * scale), hip_y + leg_len)], width=9)
    draw_wobbly_line(draw, [(cx, hip_y), (cx + int(80 * scale), hip_y + leg_len)], width=9)

def generate_zenn_style_thumbnail(
    hook_text: str,
    topic_key: str,
    out_path: Path,
    bg_color: str = "#8CB7CA" # Default soft cinematic blue/cyan
):
    """
    Builds a master 1920x1080 (16:9) YouTube cover image matching Zenn's high-CTR formula.
    """
    random.seed(42)
    im = Image.new("RGB", (1920, 1080), bg_color)
    draw = ImageDraw.Draw(im)
    
    # Ground line
    draw_wobbly_line(draw, [(0, 940), (1920, 940)], width=8)
    
    # Pick theme and artwork based on topic
    tk = topic_key.lower()
    
    if "nocebo" in tk:
        # Crimson Red Theme with "THE EVIL PLACEBO"
        im = Image.new("RGB", (1920, 1080), "#8B1E2B")
        draw = ImageDraw.Draw(im)
        draw_wobbly_line(draw, [(0, 940), (1920, 940)], width=8)
        # Giant Red Box Banner with White & Yellow Text
        font_large = get_thumbnail_font(180)
        draw_stroked_text(draw, (220, 240), "THE EVIL", font_large, fill_color="#FFFFFF", stroke_color="#000000", stroke_width=18)
        draw_stroked_text(draw, (180, 480), "PLACEBO", font_large, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
        
    elif "slotow" in tk or "elephant" in tk:
        # Soft Savanna Sand Theme: `#EAD5A0`
        im = Image.new("RGB", (1920, 1080), "#E9D8B2")
        draw = ImageDraw.Draw(im)
        draw_wobbly_line(draw, [(0, 940), (1920, 940)], width=8)
        
        # Left side: Giant Yellow Hook Text
        font_hook = get_thumbnail_font(175)
        hook_lines = hook_text.upper().split("\n")
        if len(hook_lines) == 1:
            draw_stroked_text(draw, (140, 160), hook_lines[0], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=18)
        else:
            draw_stroked_text(draw, (140, 120), hook_lines[0], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=18)
            draw_stroked_text(draw, (140, 310), hook_lines[1], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=18)
            
        # Dramatic Visual: Giant Hand reaching down or berserk juvenile elephant facing fallen rhino
        # Fallen rhino on the ground
        draw.ellipse([1100, 780, 1550, 940], fill="#D8D0C5", outline="black", width=7)
        draw_wobbly_line(draw, [(1480, 830), (1570, 780), (1550, 860)], width=8) # Broken horn
        draw.line([(1420, 810), (1450, 840)], fill="black", width=6) # Eye X
        draw.line([(1450, 810), (1420, 840)], fill="black", width=6)
        
        # Raging juvenile elephant with red rage aura
        ecx, ecy = 750, 680
        for ar in [220, 200, 180]:
            draw.ellipse([ecx - ar, ecy - ar + 40, ecx + ar, ecy + ar + 40], fill=(255, 210, 210))
        draw.ellipse([ecx - 170, ecy - 110, ecx + 170, ecy + 110], fill="#B0B8C4", outline="black", width=8)
        # Head & trunk raised aggressive
        draw_circle_wobbly(draw, ecx + 140, ecy - 50, 75, fill="#B0B8C4", width=8)
        draw_wobbly_line(draw, [(ecx + 180, ecy - 20), (ecx + 240, ecy - 90), (ecx + 230, ecy - 130)], width=10) # Trunk up
        draw.ellipse([ecx + 155, ecy - 65, ecx + 170, ecy - 50], fill=(220, 30, 30)) # Red eye
        for lx in [ecx - 110, ecx - 40, ecx + 40, ecx + 110]:
            draw_wobbly_line(draw, [(lx, ecy + 80), (lx, 940)], width=10)
        draw.text((ecx + 180, ecy - 190), "! ! !", fill=(220, 30, 30), font=get_thumbnail_font(120))
        
    elif "quietest" in tk or "room" in tk:
        # Dark Cave / Anechoic Chamber: `#18232C`
        im = Image.new("RGB", (1920, 1080), "#18232C")
        draw = ImageDraw.Draw(im)
        draw_wobbly_line(draw, [(0, 940), (1920, 940)], fill="#304050", width=8)
        font_hook = get_thumbnail_font(180)
        draw_stroked_text(draw, (380, 160), "GO CRAZY?", font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
        draw_thumbnail_stickman(draw, 960, 640, scale=1.4, expression="sweat")
        
    elif "voice" in tk:
        # Soft Teal/Cyan: `#8CB7CA`
        im = Image.new("RGB", (1920, 1080), "#8CB7CA")
        draw = ImageDraw.Draw(im)
        draw_wobbly_line(draw, [(0, 940), (1920, 940)], width=8)
        font_hook = get_thumbnail_font(180)
        draw_stroked_text(draw, (340, 140), "THAT'S ME?", font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
        draw_thumbnail_stickman(draw, 720, 620, scale=1.3, expression="sweat")
        # Phone on table vibrating
        draw.rectangle([1150, 520, 1380, 880], fill="#EAECEE", outline="black", width=8)
        draw.polygon([(1220, 640), (1220, 740), (1310, 690)], fill="#2196F3", outline="black")
        for vy in [560, 620, 680, 740, 800]:
            draw.arc([1390, vy - 20, 1440, vy + 20], 270, 90, fill="black", width=6)
            
    else:
        # Universal High-CTR Template
        font_hook = get_thumbnail_font(175)
        hook_lines = hook_text.upper().split("\n")
        if len(hook_lines) == 1:
            draw_stroked_text(draw, (160, 150), hook_lines[0], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
        else:
            draw_stroked_text(draw, (160, 110), hook_lines[0], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
            draw_stroked_text(draw, (160, 300), hook_lines[1], font_hook, fill_color="#FFE600", stroke_color="#000000", stroke_width=20)
            
        draw_thumbnail_stickman(draw, 1280, 620, scale=1.35, expression="questioning")
        
    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=95)
    print(f"  -> Generated High-CTR Cover Image: {out_path}")
    return out_path

if __name__ == "__main__":
    test_out = Path("output/test_thumbnail_slotow.png")
    generate_zenn_style_thumbnail("NO ADULTS?", "slotow_effect", test_out)
