import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_font(font_name: str, size: int) -> ImageFont.ImageFont:
    paths = [
        Path(f"C:/Windows/Fonts/{font_name}"),
        Path(f"C:/Windows/Fonts/impact.ttf"),
        Path(f"C:/Windows/Fonts/arialbd.ttf")
    ]
    for p in paths:
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_wobbly_line(draw: ImageDraw.ImageDraw, points, fill="black", width=6, roughness=2.0):
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

def draw_circle_wobbly(draw: ImageDraw.ImageDraw, cx, cy, r, fill=None, outline="black", width=6):
    num_pts = 32
    pts = []
    for i in range(num_pts):
        angle = 2 * math.pi * i / num_pts
        cur_r = r + random.uniform(-2.5, 2.5)
        pts.append((cx + cur_r * math.cos(angle), cy + cur_r * math.sin(angle)))
    pts.append(pts[0])
    if fill:
        draw.polygon(pts, fill=fill)
    draw_wobbly_line(draw, pts, fill=outline, width=width)

# =============================================================================
# 1. PROFILE LOGO / AVATAR GENERATOR (800x800)
# =============================================================================
def generate_channel_logo(out_path: Path, bg_color: str = "#8C1E1F"):
    """
    Builds an 800x800 circular profile icon matching the Zenn-style aesthetic.
    Deep crimson circular background with iconic hand-drawn thinker doodle.
    """
    random.seed(101)
    im = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    
    # Outer circular badge
    draw.ellipse([20, 20, 780, 780], fill=bg_color)
    
    # Subtle inner concentric ring
    draw.ellipse([35, 35, 765, 765], outline=(255, 255, 255, 50), width=4)
    
    # Hand-drawn Thinker Doodle in center
    cx, cy = 400, 430
    
    # Glowing Idea Bulb above head
    bulb_cx, bulb_cy = 400, 190
    draw.ellipse([bulb_cx - 40, bulb_cy - 45, bulb_cx + 40, bulb_cy + 35], fill="#FFE600", outline="black", width=6)
    draw.rectangle([bulb_cx - 18, bulb_cy + 35, bulb_cx + 18, bulb_cy + 55], fill="#E0E0E0", outline="black", width=5)
    # Sparks
    for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(ang)
        x1 = bulb_cx + 55 * math.cos(rad)
        y1 = bulb_cy + 55 * math.sin(rad)
        x2 = bulb_cx + 80 * math.cos(rad)
        y2 = bulb_cy + 80 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill="#FFE600", width=6)
        
    # Head
    draw_circle_wobbly(draw, cx, cy - 70, 95, fill="#FFFFFF", width=8)
    
    # Eyes (observant / looking up toward the lightbulb)
    draw.ellipse([cx - 40, cy - 90, cx - 20, cy - 70], fill="black")
    draw.ellipse([cx + 20, cy - 90, cx + 40, cy - 70], fill="black")
    # Eyebrows raised
    draw.arc([cx - 50, cy - 115, cx - 10, cy - 95], 180, 360, fill="black", width=6)
    draw.arc([cx + 10, cy - 115, cx + 50, cy - 95], 180, 360, fill="black", width=6)
    # Calm smiling mouth
    draw.arc([cx - 30, cy - 60, cx + 30, cy - 30], 0, 180, fill="black", width=6)
    
    # Body (Torso)
    draw_wobbly_line(draw, [(cx, cy + 25), (cx, cy + 220)], width=10)
    
    # Arms in thinking / eureka pose
    # Left hand resting under chin
    draw_wobbly_line(draw, [(cx, cy + 60), (cx - 85, cy + 120), (cx - 20, cy + 30)], width=9)
    # Right arm resting on hip
    draw_wobbly_line(draw, [(cx, cy + 60), (cx + 90, cy + 130), (cx + 5, cy + 190)], width=9)
    
    # Minimalist 'S' brandmark monogram at bottom
    f_brand = get_font("impact.ttf", 68)
    draw.text((cx - 22, 675), "S", fill="#FFFFFF", font=f_brand)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Convert RGBA to RGB with white background for YouTube standard upload
    final_rgb = Image.new("RGB", (800, 800), "#111111")
    final_rgb.paste(im, (0, 0), im)
    final_rgb.save(out_path, quality=98)
    print(f"  -> Generated Channel Logo: {out_path}")
    return out_path

# =============================================================================
# 2. CHANNEL BANNER GENERATOR (2560x1440 YouTube Standard)
# =============================================================================
def generate_channel_banner(out_path: Path):
    """
    Builds a 2560x1440 YouTube channel banner with all key branding locked inside
    the mobile/desktop universal safe zone (1546 x 423 pixels in the exact center).
    """
    random.seed(202)
    # Dark cinematic obsidian background
    im = Image.new("RGB", (2560, 1440), "#121519")
    draw = ImageDraw.Draw(im)
    
    # Subtle background constellation / grid dots
    for _ in range(85):
        rx = random.randint(100, 2460)
        ry = random.randint(100, 1340)
        draw.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill=(255, 255, 255, 60))
        
    # Safe area coordinates: Center X=1280, Y=720, Width=1546, Height=423
    safe_left = (2560 - 1546) // 2   # 507
    safe_right = safe_left + 1546    # 2053
    safe_top = (1440 - 423) // 2     # 508
    safe_bottom = safe_top + 423     # 931
    
    # Ground horizon line running across the safe area
    horizon_y = safe_bottom - 45
    draw_wobbly_line(draw, [(safe_left - 300, horizon_y), (safe_right + 300, horizon_y)], fill="#2A323D", width=6)
    
    # Center Brand Title: STATESIDE
    f_title = get_font("impact.ttf", 125)
    f_tagline = get_font("arialbd.ttf", 36)
    f_schedule = get_font("arialbd.ttf", 26)
    
    # Title centered vertically and horizontally in safe zone
    title_text = "STATESIDE"
    bbox = draw.textbbox((0, 0), title_text, font=f_title)
    tw = bbox[2] - bbox[0]
    tx = (2560 - tw) // 2
    ty = 580
    
    # Drop shadow
    draw.text((tx + 5, ty + 5), title_text, fill="#000000", font=f_title)
    # Main Title
    draw.text((tx, ty), title_text, fill="#FFFFFF", font=f_title)
    
    # Tagline
    tag_text = "THE HIDDEN MECHANICS OF HUMAN NATURE"
    tbox = draw.textbbox((0, 0), tag_text, font=f_tagline)
    tag_x = (2560 - (tbox[2] - tbox[0])) // 2
    tag_y = ty + 145
    draw.text((tag_x, tag_y), tag_text, fill="#FFE600", font=f_tagline)
    
    # Sub-detail: Psychology • Evolution • Deep Science
    sub_text = "PSYCHOLOGY   •   ANIMAL BEHAVIOR   •   DEEP SCIENCE"
    sbox = draw.textbbox((0, 0), sub_text, font=f_schedule)
    sub_x = (2560 - (sbox[2] - sbox[0])) // 2
    sub_y = tag_y + 55
    draw.text((sub_x, sub_y), sub_text, fill="#8E9DAF", font=f_schedule)
    
    # Left Vignette (Inside Safe Area): The Thinker observing an illuminated Brain diagram
    lx = safe_left + 180
    ly = horizon_y
    # Brain doodle on easel/stand
    brain_cx, brain_cy = lx + 140, ly - 150
    draw_circle_wobbly(draw, brain_cx - 40, brain_cy, 60, fill="#24141E", outline="#FF4081", width=5)
    draw_circle_wobbly(draw, brain_cx + 40, brain_cy, 60, fill="#24141E", outline="#FF4081", width=5)
    draw.line([(brain_cx, brain_cy + 60), (brain_cx - 40, ly)], fill="#8E9DAF", width=5)
    draw.line([(brain_cx, brain_cy + 60), (brain_cx + 40, ly)], fill="#8E9DAF", width=5)
    # Observer stickman with magnifying glass
    draw_circle_wobbly(draw, lx, ly - 180, 48, fill="#FFFFFF", outline="white", width=6)
    draw.line([(lx, ly - 132), (lx, ly - 40)], fill="white", width=7)
    draw.line([(lx, ly - 40), (lx - 35, ly)], fill="white", width=7)
    draw.line([(lx, ly - 40), (lx + 35, ly)], fill="white", width=7)
    draw.line([(lx, ly - 100), (lx + 50, ly - 120)], fill="white", width=6)
    # Magnifying glass
    draw.ellipse([lx + 45, ly - 145, lx + 85, ly - 105], outline="#FFE600", width=6)
    draw.line([(lx + 75, ly - 110), (lx + 95, ly - 90)], fill="#FFE600", width=6)
    
    # Right Vignette (Inside Safe Area): Observer with Telescope pointed at stars
    rx = safe_right - 220
    ry = horizon_y
    # Telescope on tripod
    tele_x, tele_y = rx - 90, ry - 110
    draw.line([(tele_x - 30, ry), (tele_x, tele_y)], fill="#8E9DAF", width=5)
    draw.line([(tele_x + 30, ry), (tele_x, tele_y)], fill="#8E9DAF", width=5)
    draw.line([(tele_x - 40, tele_y + 20), (tele_x + 50, tele_y - 30)], fill="#42A5F5", width=12) # Barrel
    # Observer looking through eyepiece
    draw_circle_wobbly(draw, rx, ry - 170, 48, fill="#FFFFFF", outline="white", width=6)
    draw.line([(rx, ry - 122), (rx, ry - 40)], fill="white", width=7)
    draw.line([(rx, ry - 40), (rx - 30, ry)], fill="white", width=7)
    draw.line([(rx, ry - 40), (rx + 30, ry)], fill="white", width=7)
    draw.line([(rx, ry - 90), (rx - 50, tele_y)], fill="white", width=6)
    # Starburst above
    for sa in range(0, 360, 45):
        srad = math.radians(sa)
        draw.line([
            (tele_x + 90 + 15 * math.cos(srad), tele_y - 65 + 15 * math.sin(srad)),
            (tele_x + 90 + 35 * math.cos(srad), tele_y - 65 + 35 * math.sin(srad))
        ], fill="#FFE600", width=5)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    im.save(out_path, quality=95)
    print(f"  -> Generated Channel Banner: {out_path}")
    return out_path

if __name__ == "__main__":
    logo_file = Path("output/branding/stateside_profile_logo.png")
    banner_file = Path("output/branding/stateside_channel_banner.png")
    generate_channel_logo(logo_file)
    generate_channel_banner(banner_file)
    print("Branding generation complete!")
