"""Daily specials v3.1 graphics: feed 1080x1350, story 1080x1920, screen 1080x1920 (in-store, read from 3-4 m).
Critic-round fixes: no Roman numerals; split SAVE line (gold) and add-on line (muted); bigger time; food sits higher
(stage sized to the tallest dish); screen minimum 38 px text; story price/time kept above y=1580."""
import os, sys
sys.path.insert(0, "/home/claude/gen")
from PIL import Image, ImageDraw
import specials as SP
from specials_data import SPECIALS, EXTRA, window

LN = ["lnum", "pnum"]
CREAM = SP.HEAD

def build_stage(specs, cups, mode, max_w):
    big = mode != "feed"
    multi = len(specs) > 1
    area = {'feed': 270000, 'story': 370000, 'screen': 430000}[mode] * (0.55 if multi else 1)
    maxh = {'feed': 420, 'story': 420, 'screen': 560}[mode]
    mw = (660 if big else 560) if not multi else (520 if big else 430)
    layers = [SP.dish_layer(SP.SRC + p, mw, int(maxh * (0.85 if 'Salmon & Guac' in p else 1)), area * (0.8 if 'Salmon & Guac' in p else 1)) for p in specs]
    if multi:  # second dish at 0.8x height of the first
        l0, l1 = layers[0], layers[1]; k = (l0.height * 1.15) / l1.height
        layers[1] = l1.resize((int(l1.width * k), int(l1.height * k)), Image.LANCZOS)
    cupsz = 300 if big else 230
    cl = [SP.cup(cupsz, k) for k in cups]
    gap = 30 if multi else 0
    def width(): return sum(l.width for l in layers) + gap * (len(layers) - 1) + (int(cupsz * .62) if cl else 0)
    w = width()
    if w > max_w:
        k = max_w / w
        layers = [l.resize((int(l.width * k), int(l.height * k)), Image.LANCZOS) for l in layers]; w = width()
    h = max([l.height for l in layers] + ([int(cupsz * .8)] if cl else []))
    st = Image.new("RGBA", (w + 20, h + 10), (0, 0, 0, 0)); shadows = []
    x = 0
    for l in layers:
        shadows.append((x + l.width * .08, h - 14, l.width * .84, 30))
        st.paste(l, (x, h - l.height + 6), l); x += l.width + gap
    if cl:
        x -= gap + int(cupsz * .2)
        st.paste(cl[0], (x, h - int(cupsz * .80)), cl[0])
    return st, shadows, h

def render(sp, mode="feed", extra=False, yoff=None):
    W, H = (1080, 1350) if mode == "feed" else (1080, 1920)
    story = mode == "story"; big = mode != "feed"
    im = SP.bg(W, H); d = ImageDraw.Draw(im, "RGBA"); SP.frame(d, W, H); cx = W // 2
    y = {"feed": 92, "story": 230, "screen": 170}[mode] + (yoff or 0)
    hm = Image.open(SP.HEADMARK).convert("RGBA"); hw = {"feed": 104, "story": 124, "screen": 130}[mode]
    hm = hm.resize((hw, int(hm.height * hw / hm.width)), Image.LANCZOS)
    im.paste(hm, (cx - hw // 2, y), hm); d = ImageDraw.Draw(im, "RGBA")
    y += hm.height + (30 if big else 26)
    kick = (sp["days"] if extra else sp["day"]).upper()
    rf = SP.SC({"feed": 34, "story": 40, "screen": 52}[mode]); rw = d.textlength(kick, font=rf)
    ly = y + rf.size * 0.62
    d.line((cx - rw / 2 - 70, ly, cx - rw / 2 - 18, ly), fill=SP.GOLD, width=2)
    d.line((cx + rw / 2 + 18, ly, cx + rw / 2 + 70, ly), fill=SP.GOLD, width=2)
    SP.ctext(d, cx, y, kick, rf, SP.GOLD)
    y += int(rf.size * 1.55)
    tf = SP.DISP({"feed": 112, "story": 136, "screen": 140}[mode])
    while d.textlength(sp["name"], font=tf) > W - 200: tf = SP.DISP(tf.size - 4)
    SP.ctext(d, cx, y, sp["name"], tf, CREAM); y += int(tf.size * 1.14)
    sf = SP.EBI({"feed": 42, "story": 48, "screen": 52}[mode]); sub = sp["pair"]
    while d.textlength(sub, font=sf, features=LN) > W - 220: sf = SP.EBI(sf.size - 2)
    d.text((cx - d.textlength(sub, font=sf, features=LN) / 2, y), sub, font=sf, fill=SP.BODYC, features=LN)
    y += int(sf.size * 1.25) + (40 if big else 34)
    if extra:
        c = SP.cup(300 if big else 240, "latte"); sh = int(c.height * .86)
        im.paste(c, (cx - c.width // 2 + 18, y), c); base = y + sh
        d = ImageDraw.Draw(im, "RGBA")
        cf = SP.EBI({"feed": 34, "story": 40, "screen": 44}[mode]); base += 30; t = sp["cakes"]
        while d.textlength(t, font=cf) > W - 200: cf = SP.EBI(cf.size - 2)
        SP.ctext(d, cx, base, t, cf, SP.BODYC); base += int(cf.size * 1.4)
    else:
        st, shadows, sh = build_stage(sp["dishes"], sp["cups"], mode, W - 240)
        sx = cx - (st.width - 20) // 2
        for (a, b, w_, h_) in shadows: SP.shadow(im, sx + a, y + b, w_, h_, alpha=150, blur=16)
        im.paste(st, (sx, y), st); base = y + sh
    d = ImageDraw.Draw(im, "RGBA")
    d.line((cx - 360, base + 6, cx + 360, base + 6), fill=SP.GOLD + (110,), width=1)
    y = base + {"feed": 34, "story": 44, "screen": 50}[mode]
    pf = SP.DISP({"feed": 132, "story": 170, "screen": 200}[mode]); dol = SP.DISP(int(pf.size * .45)); p = sp["price"]
    pw = d.textlength(p, font=pf, features=LN); dw = d.textlength("$", font=dol); x0 = cx - (pw + dw + 8) / 2
    d.text((x0, y + int(pf.size * .155)), "$", font=dol, fill=SP.GOLD)
    d.text((x0 + dw + 8, y), p, font=pf, fill=SP.GOLD, features=LN)
    y += int(pf.size * 1.08)
    gf = SP.JOST({"feed": 34, "story": 44, "screen": 56}[mode])
    SP.ctext(d, cx, y, sp["save"], gf, SP.GOLD, sp=5); y += int(gf.size * 1.5)
    if sp.get("inc"):
        mf = SP.JOST({"feed": 26, "story": 30, "screen": 38}[mode]); t = sp["inc"]
        while d.textlength(t, font=mf) + 4 * len(t) > W - 180: mf = SP.JOST(mf.size - 1)
        SP.ctext(d, cx, y, t, mf, SP.MUTED, sp=4); y += int(mf.size * 1.5)
    when = window(sp)
    if mode == "feed":
        SP.ctext(d, cx, H - 132, f"{when.upper()}  ·  290 GERRARD ST E", SP.JOST(32), CREAM, sp=4)
    elif story:
        y += 16; SP.rule(d, cx, y); y += 34
        t = f"Served {when}, while it lasts"; f = SP.EBI(42)
        d.text((cx - d.textlength(t, font=f, features=LN) / 2, y), t, font=f, fill=SP.BODYC, features=LN)
        endy = y + 50
        if yoff is None:  # centre the whole block in the story safe area (250..1560)
            off = max(0, int((250 + 1560 - (endy - 230)) / 2 - 230))
            return render(sp, mode, extra, off)
        if endy > 1580: print("WARN story low:", sp["name"], endy)
    else:
        y += 20; SP.rule(d, cx, y, half=200); y += 40
        t = f"Served {when}"; f = SP.EBI(58)
        d.text((cx - d.textlength(t, font=f, features=LN) / 2, y), t, font=f, fill=CREAM, features=LN)
        SP.ctext(d, cx, H - 120, "290 GERRARD ST E  ·  EPOSBAR.COM", SP.JOST(30), SP.MUTED, sp=4)
    return im

def thumb(sp, size=192):
    im = Image.new("RGB", (size * 2, size * 2), SP.INK)
    st, _, _ = build_stage(sp["dishes"], [], "feed", 2000)
    k = min((size * 2 - 40) / st.width, (size * 2 - 40) / st.height)
    st = st.resize((int(st.width * k), int(st.height * k)), Image.LANCZOS)
    im.paste(st, ((im.width - st.width) // 2, (im.height - st.height) // 2), st)
    return im.resize((size, size), Image.LANCZOS)

if __name__ == "__main__":
    out = "/mnt/user-data/outputs/specials-v3"; os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    for i, sp in enumerate(SPECIALS, 1):
        render(sp, "story").save(f"{out}/story-{i}-{sp['day']}.jpg", quality=92)
        render(sp, "feed").save(f"{out}/feed-{i:02d}-{sp['day']}.jpg", quality=92)
        render(sp, "screen").save(f"{out}/screen-special-{i}-{sp['day']}.jpg", quality=92)
        thumb(sp).save(f"/home/claude/site2/img/specials/{sp['img']}-thumb.webp", quality=86)
    render(EXTRA, "story", extra=True).save(f"{out}/story-8-Coffee-and-Cake.jpg", quality=92)
    render(EXTRA, "screen", extra=True).save(f"{out}/screen-special-8-Coffee-and-Cake.jpg", quality=92)
    print("ok")
