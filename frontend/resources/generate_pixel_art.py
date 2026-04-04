"""
Generate pixel art characters for 5 digital nomad persona types.
All characters face RIGHT (side profile view).
All share the same base body proportions (wanderer standard).
Style: 16x16 pixel art → 512x512 (x32) + 64x64 (x4).
"""
from PIL import Image
import os

CANVAS = 16
SCALE_BIG = 32
SCALE_SM = 4

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PALETTES = {
    "wanderer": {
        "name": "거침없는 나그네",
        "skin": (255, 214, 170), "skin_s": (230, 185, 140),
        "hair": (60, 40, 30),
        "pri": (230, 80, 50), "pri_d": (190, 60, 35),
        "sec": (255, 160, 60), "sec_d": (220, 130, 40),
        "acc": (180, 50, 30),
        "boot": (100, 60, 40), "eye": (40, 30, 20),
    },
    "local": {
        "name": "어디서든 현지인",
        "skin": (240, 200, 160), "skin_s": (215, 175, 135),
        "hair": (80, 50, 30),
        "pri": (70, 160, 120), "pri_d": (50, 130, 95),
        "sec": (120, 200, 160), "sec_d": (90, 170, 130),
        "acc": (50, 120, 90),
        "boot": (90, 70, 50), "eye": (40, 30, 20),
    },
    "planner": {
        "name": "영리한 설계자",
        "skin": (245, 220, 190), "skin_s": (220, 195, 165),
        "hair": (40, 40, 50),
        "pri": (60, 100, 180), "pri_d": (40, 75, 150),
        "sec": (100, 150, 220), "sec_d": (70, 120, 190),
        "acc": (40, 70, 140),
        "boot": (60, 50, 50), "eye": (30, 30, 40),
    },
    "free_spirit": {
        "name": "자유로운 영혼",
        "skin": (250, 210, 175), "skin_s": (225, 185, 150),
        "hair": (160, 100, 60),
        "pri": (200, 140, 220), "pri_d": (170, 110, 190),
        "sec": (240, 180, 255), "sec_d": (180, 130, 200),
        "acc": (150, 90, 180),
        "boot": (120, 90, 70), "eye": (50, 30, 40),
    },
    "pioneer": {
        "name": "용감한 개척자",
        "skin": (235, 200, 165), "skin_s": (210, 175, 140),
        "hair": (30, 30, 30),
        "pri": (220, 170, 50), "pri_d": (190, 145, 35),
        "sec": (255, 210, 80), "sec_d": (200, 155, 40),
        "acc": (180, 130, 30),
        "boot": (70, 50, 40), "eye": (30, 25, 20),
    },
}


def new_img():
    return Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))


def px(im, x, y, c):
    if 0 <= x < CANVAS and 0 <= y < CANVAS:
        im.putpixel((x, y), c if len(c) == 4 else (*c, 255))


# =====================================================================
# SHARED BASE — wanderer 기준 체형
#   Hair top : y=2, x=6-9        (top of head hair)
#   Hair back: x=5, y=4-5        (back hair)
#   Head     : y=4-6, x=6-9      (3 rows, 4 cols)
#   Nose     : x=10, y=4-5       (protrusion)
#   Eye      : x=9, y=5
#   Mouth    : x=10, y=6
#   Body     : y=7-9, x=6-9      (3 rows, 4 cols)
#   Legs     : y=10-12            (wanderer walk cycle)
# =====================================================================
def draw_base(im, p, f, walk=True):
    """Draw shared body. Returns arm_dy for accessory positioning."""
    arm_dy = [0, -1, 0, 1][f % 4] if walk else 0

    # --- Hair (default short, back) ---
    px(im, 5, 4, p["hair"]); px(im, 5, 5, p["hair"])
    for x in range(6, 10): px(im, x, 3, p["hair"])

    # --- Head (side profile → right) ---
    for y in range(4, 7):
        for x in range(6, 10): px(im, x, y, p["skin"])
    px(im, 10, 4, p["skin"]); px(im, 10, 5, p["skin"])  # nose
    px(im, 6, 4, p["skin_s"])  # back shadow

    # Eye
    px(im, 9, 5, p["eye"])

    # --- Body ---
    for y in range(7, 10):
        for x in range(6, 10): px(im, x, y, p["pri"])
    px(im, 6, 7, p["pri_d"]); px(im, 6, 8, p["pri_d"])  # back shadow

    # --- Legs (wanderer walk cycle) ---
    if walk:
        if f == 0:
            px(im, 6, 10, p["acc"]); px(im, 6, 11, p["acc"]); px(im, 6, 12, p["boot"])
            px(im, 9, 10, p["acc"]); px(im, 9, 11, p["acc"]); px(im, 9, 12, p["boot"])
        elif f == 1:
            px(im, 7, 10, p["acc"]); px(im, 7, 11, p["acc"]); px(im, 7, 12, p["boot"])
            px(im, 8, 10, p["acc"]); px(im, 8, 11, p["acc"]); px(im, 8, 12, p["boot"])
        elif f == 2:
            px(im, 9, 10, p["acc"]); px(im, 9, 11, p["acc"]); px(im, 9, 12, p["boot"])
            px(im, 6, 10, p["acc"]); px(im, 6, 11, p["acc"]); px(im, 6, 12, p["boot"])
        else:
            px(im, 7, 10, p["acc"]); px(im, 7, 11, p["acc"]); px(im, 7, 12, p["boot"])
            px(im, 8, 10, p["acc"]); px(im, 8, 11, p["acc"]); px(im, 8, 12, p["boot"])

    return arm_dy


# =====================================================================
# WANDERER — 거침없는 나그네: 새싹 모자 + 큰 배낭 + 걷기
# =====================================================================
def draw_wanderer(p, f=0):
    im = new_img()
    arm_dy = draw_base(im, p, f)

    hat = (180, 150, 100); hat_d = (140, 115, 70)
    leaf = (80, 190, 80); leaf_d = (50, 150, 50); stem = (100, 130, 60)
    leaf_sway = [0, 1, 0, -1][f % 4]

    # Round adventure hat (overwrites default hair top)
    for x in range(6, 10): px(im, x, 2, hat)
    for x in range(5, 11): px(im, x, 3, hat)
    px(im, 5, 3, hat_d); px(im, 10, 3, hat_d)
    px(im, 7, 2, hat_d)

    # Sprout leaf on top 🌱
    px(im, 8, 1, stem)
    px(im, 8 + leaf_sway, 0, leaf)
    px(im, 9 + leaf_sway, 0, leaf_d)

    # Mouth
    px(im, 10, 6, (200, 120, 100))

    # Backpack (behind)
    for y in range(5, 10):
        px(im, 4, y, p["sec"]); px(im, 3, y, p["sec"])
    px(im, 3, 5, p["sec_d"]); px(im, 3, 6, p["sec_d"])
    px(im, 3, 9, p["sec_d"]); px(im, 4, 9, p["sec_d"])
    px(im, 4, 7, (200, 200, 200))  # buckle
    px(im, 8, 7, p["acc"]); px(im, 7, 8, p["acc"])  # strap
    px(im, 3, 4, (130, 160, 130)); px(im, 4, 4, (130, 160, 130))  # rolled mat

    # Front arm (swinging)
    px(im, 10, 7 + arm_dy, p["pri"])
    px(im, 10, 8 + arm_dy, p["skin"])
    if f in (0, 2):
        px(im, 11, 8 + arm_dy, (255, 240, 200))  # map

    return im


# =====================================================================
# LOCAL — 어디서든 현지인: 커피 + 손 흔들기
# =====================================================================
def draw_local(p, f=0):
    im = new_img()
    arm_dy = draw_base(im, p, f)

    wave = [0, -1, -2, -1][f % 4]

    # Longer back hair (overwrites default)
    px(im, 5, 4, p["hair"]); px(im, 5, 5, p["hair"]); px(im, 5, 6, p["hair"])
    for x in range(6, 10): px(im, x, 3, p["hair"])
    px(im, 10, 3, p["hair"])  # front fringe

    # Warm smile
    px(im, 10, 6, (180, 110, 90))

    # Apron detail
    px(im, 7, 9, p["sec"]); px(im, 8, 9, p["sec"]); px(im, 9, 9, p["sec"])

    # Back arm + coffee cup
    px(im, 5, 7, p["pri"]); px(im, 5, 8, p["skin"])
    px(im, 4, 7, (180, 140, 100)); px(im, 4, 8, (180, 140, 100))
    px(im, 3, 8, (160, 120, 80))  # handle
    if f % 2 == 0:
        px(im, 4, 6, (220, 220, 220, 160))  # steam

    # Front arm (waving)
    px(im, 10, 7, p["pri"])
    px(im, 11, 6 + wave, p["skin"])
    px(im, 11, 5 + wave, p["skin"])
    if f in (0, 2):
        px(im, 12, 5 + wave, p["skin"])  # hand open

    return im


# =====================================================================
# PLANNER — 영리한 설계자: 안경 + 노트북
# =====================================================================
def draw_planner(p, f=0):
    im = new_img()
    draw_base(im, p, f)

    # Neat hair (overwrites default)
    px(im, 5, 4, p["hair"]); px(im, 5, 5, p["hair"])
    for x in range(6, 10): px(im, x, 3, p["hair"])

    # Glasses (side view)
    px(im, 8, 5, p["sec"]); px(im, 9, 5, p["sec"]); px(im, 10, 5, p["sec"])
    px(im, 9, 5, p["eye"])  # eye behind lens
    px(im, 7, 5, p["sec_d"])  # arm of glasses

    # Mouth
    px(im, 10, 6, (200, 150, 130))

    # Collar + tie
    px(im, 9, 7, (240, 240, 240))
    px(im, 9, 8, p["acc"])

    # Back arm
    px(im, 5, 7, p["pri"]); px(im, 5, 8, p["skin"])

    # Front arm holding laptop
    px(im, 10, 7, p["pri"]); px(im, 10, 8, p["skin"])

    # Laptop screen (side view)
    px(im, 11, 7, (60, 60, 70)); px(im, 11, 8, (60, 60, 70))
    colors = [(100, 200, 255), (130, 255, 130), (255, 200, 100)]
    px(im, 11, 7, colors[f % 3])  # screen glow

    return im


# =====================================================================
# FREE SPIRIT — 자유로운 영혼: 긴 머리 + 꽃 + 걷기
# =====================================================================
def draw_free_spirit(p, f=0):
    im = new_img()
    arm_dy = draw_base(im, p, f)

    # Long flowing hair (overwrites default)
    px(im, 4, 4, p["hair"]); px(im, 4, 5, p["hair"])
    px(im, 4, 6, p["hair"]); px(im, 4, 7, p["hair"])
    px(im, 5, 3, p["hair"]); px(im, 5, 4, p["hair"]); px(im, 5, 5, p["hair"])
    for x in range(6, 10): px(im, x, 3, p["hair"])
    # Hair tip sways
    if f in (0, 2):
        px(im, 3, 8, p["hair"])
    else:
        px(im, 4, 8, p["hair"])

    # Flower in hair 🌸
    flower = (255, 160, 200); flower_c = (255, 220, 100)
    px(im, 10, 3, flower)
    px(im, 11, 3, flower)
    px(im, 10, 4, flower)
    px(im, 11, 4, flower_c)  # center

    # Closed eye (peaceful)
    px(im, 9, 5, p["acc"])  # overwrite eye to closed line

    # Serene smile
    px(im, 10, 6, (200, 140, 120))

    # Robe/dress slightly wider
    px(im, 5, 8, p["pri"]); px(im, 5, 9, p["pri"])
    px(im, 10, 9, p["sec"])

    # Back arm relaxed
    px(im, 5, 7, p["pri_d"])

    # Front arm swinging gently
    px(im, 10, 7 + arm_dy, p["pri"])
    px(im, 10, 8 + arm_dy, p["skin"])

    # Sparkles
    sparkles = [(2, 5), (12, 7), (3, 10), (13, 3), (1, 8)]
    for i, (sx, sy) in enumerate(sparkles):
        if (i + f) % 3 == 0:
            px(im, sx, sy, (255, 255, 200, 180))

    return im


# =====================================================================
# PIONEER — 용감한 개척자: 깃발 + 나침반
# =====================================================================
def draw_pioneer(p, f=0):
    im = new_img()
    arm_dy = draw_base(im, p, f)

    # Short strong hair (overwrites default)
    px(im, 5, 4, p["hair"]); px(im, 5, 5, p["hair"])
    for x in range(6, 10): px(im, x, 3, p["hair"])

    # Thick brow
    px(im, 9, 4, p["eye"]); px(im, 10, 4, p["eye"])

    # Firm mouth
    px(im, 10, 6, (190, 135, 110))

    # Shoulder pads
    px(im, 5, 7, p["sec"]); px(im, 10, 7, p["sec"])

    # Belt + buckle
    px(im, 7, 9, p["acc"]); px(im, 8, 9, p["acc"]); px(im, 9, 9, p["acc"])
    px(im, 8, 9, p["sec"])

    # Back arm holding flag pole
    px(im, 5, 7, p["pri"]); px(im, 5, 8, p["skin"])
    # Pole
    for y in range(1, 8): px(im, 4, y, (140, 100, 60))
    # Flag (waving left)
    fw = f % 4
    for row in range(3):
        off = 0
        if fw == 1 and row == 1: off = -1
        elif fw == 3 and row == 0: off = -1
        c = p["pri"] if row < 2 else p["sec"]
        px(im, 2 + off, 1 + row, c)
        px(im, 3 + off, 1 + row, c)
    px(im, 1, 1, p["acc"])

    # Front arm + compass
    px(im, 10, 7 + arm_dy, p["pri"])
    px(im, 10, 8 + arm_dy, p["skin"])
    px(im, 11, 8 + arm_dy, (200, 180, 140))
    ndx, ndy = [(1, 0), (0, -1), (-1, 0), (0, 1)][f % 4]
    px(im, 11 + ndx, 8 + arm_dy + ndy, (230, 50, 50))

    return im


DRAW_FUNCS = {
    "wanderer": draw_wanderer,
    "local": draw_local,
    "planner": draw_planner,
    "free_spirit": draw_free_spirit,
    "pioneer": draw_pioneer,
}

NUM_FRAMES = 4
FRAME_DURATION = 300


def get_bbox(im):
    bbox = im.getbbox()
    return bbox if bbox else (0, 0, im.width, im.height)


def center_frames(raw_frames):
    min_x, min_y = CANVAS, CANVAS
    max_x, max_y = 0, 0
    for fr in raw_frames:
        b = get_bbox(fr)
        min_x, min_y = min(min_x, b[0]), min(min_y, b[1])
        max_x, max_y = max(max_x, b[2]), max(max_y, b[3])

    dx = (CANVAS - (max_x - min_x)) // 2 - min_x
    dy = (CANVAS - (max_y - min_y)) // 2 - min_y

    out = []
    for fr in raw_frames:
        c = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        for x in range(CANVAS):
            for y in range(CANVAS):
                sx, sy = x - dx, y - dy
                if 0 <= sx < CANVAS and 0 <= sy < CANVAS:
                    p = fr.getpixel((sx, sy))
                    if p[3] > 0:
                        c.putpixel((x, y), p)
        out.append(c)
    return out


def save_set(frames, folder, name, scale, suffix=""):
    scaled = [f.resize((f.width * scale, f.height * scale), Image.NEAREST) for f in frames]
    png = os.path.join(folder, f"{name}{suffix}.png")
    gif = os.path.join(folder, f"{name}{suffix}.gif")
    scaled[0].save(png)
    scaled[0].save(gif, save_all=True, append_images=scaled[1:],
                   duration=FRAME_DURATION, loop=0, disposal=2)
    return png, gif


def generate_all():
    for key, pal in PALETTES.items():
        folder = os.path.join(BASE_DIR, key)
        os.makedirs(folder, exist_ok=True)
        raw = [DRAW_FUNCS[key](pal, f) for f in range(NUM_FRAMES)]
        frames = center_frames(raw)

        p512, _ = save_set(frames, folder, key, SCALE_BIG)
        print(f"  512: {p512}")
        p64, _ = save_set(frames, folder, key, SCALE_SM, "_64")
        print(f"   64: {p64}")
        print(f"[OK] {pal['name']} ({key})")


if __name__ == "__main__":
    generate_all()
    print("\nDone!")
