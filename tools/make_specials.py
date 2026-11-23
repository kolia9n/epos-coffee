import os, sys, math
sys.path.insert(0, "/home/claude/gen")
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import make

F = "/home/claude/fonts/"
def vf(name, size, w):
    f = ImageFont.truetype(F + name, size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
DISP = lambda s: vf("CormorantGaramond%5Bwght%5D.ttf", s, 500)
ITAL = lambda s: vf("CormorantGaramond-Italic%5Bwght%5D.ttf", s, 500)
SC = lambda s: ImageFont.truetype(F + "CormorantSC-Medium.ttf", s)
JOST = lambda s: vf("Jost%5Bwght%5D.ttf", s, 500)
BODY = lambda s: vf("EBGaramond%5Bwght%5D.ttf", s, 450)
EBI = lambda s: vf("EBGaramond-Italic%5Bwght%5D.ttf", s, 450)

INK = (28, 43, 40); INK2 = (36, 54, 50); GOLD = (197, 163, 94); HEAD = (239, 228, 200); BODYC = (220, 212, 194); MUTED = (169, 179, 166)
SRC = make.SRC + "/"
HEADMARK = "/tmp/head.png"

def grain(img, amount=10):
    import random
    n = Image.effect_noise(img.size, 40).convert("L")
    n = n.point(lambda v: 128 + (v - 128) * amount // 40)
    over = Image.merge("RGB", (n, n, n))
    return Image.blend(img, Image.composite(img, over, Image.new("L", img.size, 255 - 18)), 0.5)

def bg(W, H):
    im = Image.new("RGB", (W, H), INK)
    # very soft tonal lift from top (paper-like, not a spotlight)
    lift = Image.new("L", (W, H), 0); d = ImageDraw.Draw(lift)
    for y in range(H):
        d.line((0, y, W, y), fill=int(26 * (1 - y / H)))
    im.paste(Image.new("RGB", (W, H), INK2), (0, 0), lift)
    noise = Image.effect_noise((W, H), 22).convert("L")
    noise = noise.point(lambda v: max(0, min(255, (v - 128) * 2 + 128)))
    im = Image.composite(Image.new("RGB", (W, H), (40, 60, 55)), im, noise.point(lambda v: 14 if v > 160 else 0))
    im = Image.composite(Image.new("RGB", (W, H), (20, 31, 29)), im, noise.point(lambda v: 14 if v < 96 else 0))
    return im

def frame(d, W, H, m=40):
    d.rectangle((m, m, W - m, H - m), outline=GOLD, width=2)
    d.rectangle((m + 12, m + 12, W - m - 12, H - m - 12), outline=GOLD + (110,), width=1)

def rule(d, cx, y, half=170):
    # ✱———•———✱
    d.line((cx - half + 18, y, cx - 14, y), fill=GOLD, width=2)
    d.line((cx + 14, y, cx + half - 18, y), fill=GOLD, width=2)
    d.polygon([(cx, y - 5), (cx + 5, y), (cx, y + 5), (cx - 5, y)], fill=GOLD)
    for sx in (cx - half, cx + half):
        for k in range(6):
            a = math.pi * k / 3
            d.line((sx, y, sx + 9 * math.cos(a), y + 9 * math.sin(a)), fill=GOLD, width=2)

def ctext(d, cx, y, t, f, fill, sp=0):
    if sp:
        ws = [d.textlength(c, font=f) for c in t]; tot = sum(ws) + sp * (len(t) - 1); x = cx - tot / 2
        for c, w in zip(t, ws): d.text((x, y), c, font=f, fill=fill); x += w + sp
        return
    d.text((cx - d.textlength(t, font=f) / 2, y), t, font=f, fill=fill)

def cup(size, kind="latte"):
    """Gold line-art cup on saucer, drawn at 4x and downsampled. Matches the logo's single-weight line art."""
    S = size * 4; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    lw = int(S * 0.018); g = GOLD + (255,)
    cx = S * 0.46
    if kind == "drip":
        # paper cup with sleeve and lid
        top, bot = S * 0.18, S * 0.88; wt, wb = S * 0.40, S * 0.30
        d.line((cx - wt / 2, top + S * .06, cx - wb / 2, bot), fill=g, width=lw)
        d.line((cx + wt / 2, top + S * .06, cx + wb / 2, bot), fill=g, width=lw)
        d.line((cx - wb / 2, bot, cx + wb / 2, bot), fill=g, width=lw)
        d.rounded_rectangle((cx - wt / 2 - S * .03, top, cx + wt / 2 + S * .03, top + S * .06), radius=int(S * .02), outline=g, width=lw)
        d.line((cx - wt / 2 + S * .06, top, cx - wt / 2 + S * .1, top - S * .05), fill=g, width=lw)
        d.line((cx - wt / 2 + S * .1, top - S * .05, cx + wt / 2 - S * .1, top - S * .05), fill=g, width=lw)
        d.line((cx + wt / 2 - S * .1, top - S * .05, cx + wt / 2 - S * .06, top), fill=g, width=lw)
        y1, y2 = S * .42, S * .62
        def xl(y, side): t = (y - top - S * .06) / (bot - top - S * .06); w = wt + (wb - wt) * t; return cx + side * w / 2
        d.line((xl(y1, -1), y1, xl(y1, 1), y1), fill=g, width=lw); d.line((xl(y2, -1), y2, xl(y2, 1), y2), fill=g, width=lw)
    else:
        tall = kind in ("chai", "americano")
        rim_y = S * (0.30 if tall else 0.40); base_y = S * 0.78; w = S * (0.46 if tall else 0.56)
        # saucer
        d.ellipse((cx - S * .40, base_y - S * .05, cx + S * .40, base_y + S * .09), outline=g, width=lw)
        # cup body: rim ellipse + bowl
        d.ellipse((cx - w / 2, rim_y - S * .05, cx + w / 2, rim_y + S * .05), outline=g, width=lw)
        d.arc((cx - w / 2, rim_y - (base_y - rim_y) * .9, cx + w / 2, base_y + S * .005), 0, 180, fill=g, width=lw)
        d.line((cx - w / 2, rim_y, cx - w / 2, rim_y + S * .02), fill=g, width=lw)
        # handle
        hx = cx + w / 2 - S * .02; hy = rim_y + (base_y - rim_y) * .28
        d.arc((hx - S * .06, hy - S * .02, hx + S * .14, hy + S * .16), 270, 120, fill=g, width=lw)
        # latte art leaf in the rim
        if kind in ("latte", "chai"):
            lx, ly = cx, rim_y
            d.arc((lx - S * .09, ly - S * .03, lx + S * .09, ly + S * .03), 200, 340, fill=g, width=max(2, lw // 2))
            d.arc((lx - S * .06, ly - S * .018, lx + S * .06, ly + S * .02), 200, 340, fill=g, width=max(2, lw // 2))
    return im.resize((size, size), Image.LANCZOS)

def dish_layer(path, maxw, maxh, fill_area):
    im = Image.open(path).convert("RGBA"); a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    im = im.crop(a.getbbox()); a = im.split()[3]; cov = sum(a.histogram()[41:]) / (im.width * im.height)
    s = (fill_area / (cov * im.width * im.height)) ** .5; s = min(s, maxw / im.width, maxh / im.height)
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)

def shadow(base, x, y, w, h, alpha=160, blur=22):
    sh = Image.new("L", base.size, 0)
    ImageDraw.Draw(sh).ellipse((x, y, x + w, y + h), fill=alpha)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.paste(Image.new("RGB", base.size, (10, 16, 15)), (0, 0), sh)

SPECIALS = [
    ("I", "Monday", "Egg Monday", "EPŌS Scramble", "Latte", 17, "EPŌS Scramble.png", "latte"),
    ("II", "Tuesday", "Bagel Tuesday", "Bagel sandwich", "Americano", 14, "Turkey & Gouda Bagel .png", "americano"),
    ("III", "Wednesday", "Panini Wednesday", "Hot panini", "Americano", 18, "Turkey & Gouda .png", "americano"),
    ("IV", "Thursday", "Quiche Thursday", "Quiche", "Drip Coffee", 12, "Classic Lorraine.PNG", "drip"),
    ("V", "Friday", "Croissant Friday", "Croissant sandwich", "Latte", 21, "Salmon & Guac Croissant .png", "latte"),
    ("VI", "Saturday", "Brunch Saturday", "Shakshuka", "Chai Latte", 18, "Mediterranean Shakshuka.png", "chai"),
    ("VII", "Sunday", "Sweet Sunday", "Sticky Toffee", "Latte", 15, "Sticky Toffie .png", "latte"),
]

def render(sp, W=1080, H=1920):
    rn, day, name, food, drink, price, img, cupkind = sp
    story = H > 1500
    im = bg(W, H); d = ImageDraw.Draw(im, "RGBA")
    frame(d, W, H)
    cx = W // 2
    LN = ["lnum", "pnum"]
    y = 270 if story else 96
    hm = Image.open(HEADMARK).convert("RGBA"); hw = 130 if story else 104
    hm = hm.resize((hw, int(hm.height * hw / hm.width)), Image.LANCZOS)
    im.paste(hm, (cx - hw // 2, y), hm); d = ImageDraw.Draw(im, "RGBA")
    y += hm.height + (36 if story else 26)
    # Roman numeral between short rules
    rf = SC(40 if story else 34); rw = d.textlength(rn, font=rf)
    d.line((cx - rw / 2 - 70, y + 24, cx - rw / 2 - 18, y + 24), fill=GOLD, width=2)
    d.line((cx + rw / 2 + 18, y + 24, cx + rw / 2 + 70, y + 24), fill=GOLD, width=2)
    ctext(d, cx, y, rn, rf, GOLD)
    y += 62 if story else 52
    tf = DISP(140 if story else 112)
    while d.textlength(name, font=tf) > W - 200: tf = DISP(tf.size - 4)
    ctext(d, cx, y, name, tf, HEAD)
    y += int(tf.size * 1.16)
    sub = f"{food} & {drink}"
    sf = EBI(50 if story else 42)
    d.text((cx - d.textlength(sub, font=sf, features=LN) / 2, y), sub, font=sf, fill=BODYC, features=LN)
    y += 76 if story else 58
    stage_h = 520 if story else 410
    base = y + stage_h
    dish = dish_layer(SRC + img, 700 if story else 600, stage_h, 400000 if story else 260000)
    cupsz = 290 if story else 230
    c = cup(cupsz, cupkind)
    total = dish.width + int(cupsz * .62)
    dx = cx - total // 2; dy = base - dish.height + 6
    shadow(im, dx + dish.width * .08, base - 14, dish.width * .84, 30, alpha=150, blur=16)
    im.paste(dish, (dx, dy), dish)
    cxp = dx + dish.width - int(cupsz * .2); cyp = base - int(cupsz * .80)
    im.paste(c, (cxp, cyp), c)
    d = ImageDraw.Draw(im, "RGBA")
    d.line((cx - 360, base + 4, cx + 360, base + 4), fill=GOLD + (110,), width=1)
    y = base + (56 if story else 40)
    pf = DISP(170 if story else 132); dol = DISP(76 if story else 60)
    pw = d.textlength(str(price), font=pf, features=LN); dw = d.textlength("$", font=dol)
    x0 = cx - (pw + dw + 8) / 2
    d.text((x0, y + (26 if story else 20)), "$", font=dol, fill=GOLD)
    d.text((x0 + dw + 8, y), str(price), font=pf, fill=GOLD, features=LN)
    y += int(pf.size * 1.1)
    inc = ("CHAI LATTE INCLUDED" if "Chai" in drink else "COFFEE INCLUDED")
    ctext(d, cx, y, inc, JOST(30 if story else 26), MUTED, sp=5)
    when = ("9:30 AM – 1 PM" if day == "Sunday" else "9 AM – 1 PM")
    if story:
        y += 74
        rule(d, cx, y)
        y += 40
        t = f"Served {when}, while it lasts"; f = EBI(42)
        d.text((cx - d.textlength(t, font=f, features=LN) / 2, y), t, font=f, fill=BODYC, features=LN)
    else:
        t = f"{when}  ·  290 GERRARD ST E"; f = JOST(26)
        ctext(d, cx, H - 128, t, f, MUTED, sp=4)
    return im

if __name__ == "__main__":
    out = "/mnt/user-data/outputs/specials-v2"; os.makedirs(out, exist_ok=True)
    only = sys.argv[1:] or None
    for i, sp in enumerate(SPECIALS, 1):
        if only and sp[1] not in only: continue
        render(sp).save(f"{out}/story-{i}-{sp[1]}.jpg", quality=92)
        render(sp, 1080, 1350).save(f"{out}/feed-{i:02d}-{sp[1]}.jpg", quality=92)
        print(sp[1])
