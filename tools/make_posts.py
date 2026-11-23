import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC = "/mnt/user-data/uploads/Movies/EPOS Instagram/1 Raw/Stories and extra"
LOGO = "/mnt/user-data/uploads/Movies/EPOS Instagram/Brand/epos_logo.PNG"
OUT = "/mnt/user-data/outputs/ready"
F = "/home/claude/fonts/"
TEAL = (9, 29, 23); TEAL2 = (21, 50, 40); GOLD = (201, 168, 98); CREAM = (243, 234, 216); MUTED = (169, 189, 184)

def font(name, size, w):
    f = ImageFont.truetype(F + name, size)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
SERIF = lambda s, w=600: font("CormorantGaramond%5Bwght%5D.ttf", s, w)
ITAL = lambda s, w=500: font("CormorantGaramond-Italic%5Bwght%5D.ttf", s, w)
SANS = lambda s, w=500: font("Figtree%5Bwght%5D.ttf", s, w)

def background(W, H):
    bg = Image.new("RGB", (W, H), TEAL)
    glow = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(glow)
    d.ellipse((W*0.05, H*0.12, W*0.95, H*0.78), fill=150)
    glow = glow.filter(ImageFilter.GaussianBlur(W*0.18))
    bg.paste(Image.new("RGB", (W, H), TEAL2), (0, 0), glow)
    return bg

def frame(d, W, H, m=38):
    d.rectangle((m, m, W-m, H-m), outline=GOLD, width=2)
    d.rectangle((m+10, m+10, W-m-10, H-m-10), outline=GOLD + (0,), width=1)

def ornament(d, cx, y, half=150):
    d.line((cx-half, y, cx-14, y), fill=GOLD, width=1)
    d.line((cx+14, y, cx+half, y), fill=GOLD, width=1)
    for dx in (-6, 0, 6):
        d.ellipse((cx+dx-2, y-2, cx+dx+2, y+2), fill=GOLD)

def ctext(d, cx, y, text, f, fill, spacing=0):
    if spacing:
        widths = [d.textlength(c, font=f) for c in text]
        total = sum(widths) + spacing*(len(text)-1)
        x = cx - total/2
        for c, w in zip(text, widths):
            d.text((x, y), c, font=f, fill=fill); x += w + spacing
        return
    w = d.textlength(text, font=f)
    d.text((cx - w/2, y), text, font=f, fill=fill)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def place_dish(bg, path, box, fill=0.34, align="bottom"):
    im = Image.open(path).convert("RGBA")
    a = im.split()[3].point(lambda v: 255 if v > 40 else 0)
    im = im.crop(a.getbbox()); a = im.split()[3]
    cov = a.histogram()[41:]; cov = sum(cov) / (im.width * im.height)
    x0, y0, x1, y1 = box; bw, bh = x1-x0, y1-y0
    s = ((fill * bw * bh) / (cov * im.width * im.height)) ** 0.5
    s = min(s, bw/im.width, bh/im.height)
    im = im.resize((max(1,int(im.width*s)), max(1,int(im.height*s))), Image.LANCZOS)
    px = x0 + (bw-im.width)//2
    py = (y1 - im.height) if align == "bottom" else y0 + (bh-im.height)//2
    a = im.split()[3]
    sh = Image.new("L", bg.size, 0)
    ew, eh = int(im.width*0.86), max(8, int(im.height*0.10))
    ImageDraw.Draw(sh).ellipse((px+(im.width-ew)//2, py+im.height-eh//2-4, px+(im.width+ew)//2, py+im.height+eh//2-4), fill=170)
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    bg.paste(Image.new("RGB", bg.size, (2, 12, 9)), (0, 0), sh)
    bg.paste(im, (px, py), im)

def logo_img(w):
    im = Image.open(LOGO).convert("RGBA"); im = im.crop(im.getbbox())
    s = w/im.width
    return im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)

def header(d, W, top):
    ctext(d, W/2, top, "EPŌS COFFEE BAR", SANS(22, 600), GOLD, spacing=6)

def footer(d, W, H, bottom_pad=78):
    ctext(d, W/2, H-bottom_pad, "290 GERRARD ST E  ·  @EPOS.COFFEE", SANS(19, 500), MUTED, spacing=3)

def fit_font(d, text, mk, size, maxw, minsize=40):
    while size > minsize and d.textlength(text, font=mk(size)) > maxw: size -= 2
    return mk(size)

def dish_slide(dish, name, desc, price, W=1080, H=1350, kicker=None, story=False):
    bg = background(W, H); d = ImageDraw.Draw(bg, "RGBA")
    frame(d, W, H)
    off = 0 if not story else 360
    header(d, W, 92 + off*0.5)
    if kicker: ctext(d, W/2, 132 + off*0.5, kicker.upper(), SANS(18, 500), MUTED, spacing=4)
    base = 880 + off
    place_dish(bg, os.path.join(SRC, dish), (130, 200 + off*0.55, W-130, base), fill=0.36 if not story else 0.40)
    d = ImageDraw.Draw(bg, "RGBA")
    y = base + 56
    ornament(d, W/2, y); y += 34
    nf = fit_font(d, name, lambda z: SERIF(z, 600), 70, W-220)
    ctext(d, W/2, y, name, nf, GOLD); y += 90
    df = fit_font(d, desc, lambda z: ITAL(z, 500), 34, W-240, 26)
    ctext(d, W/2, y, desc, df, CREAM); y += 66
    ctext(d, W/2, y, price, SERIF(54, 600), GOLD)
    footer(d, W, H, 78 if not story else 200)
    return bg

def cover(title, sub, dishes, W=1080, H=1350, story=False):
    bg = background(W, H); d = ImageDraw.Draw(bg, "RGBA")
    frame(d, W, H)
    off = 0 if not story else 200
    lg = logo_img(200)
    bg.paste(lg, ((W-lg.width)//2, 84 + off), lg)
    d = ImageDraw.Draw(bg, "RGBA")
    y = 84 + off + lg.height + 34
    ornament(d, W/2, y); y += 30
    lines = title.split("\n")
    tf = SERIF(84 if len(lines) == 1 else 76, 600)
    for line in lines:
        ctext(d, W/2, y, line, tf, GOLD); y += tf.size + 4
    y += 4
    ctext(d, W/2, y, sub, ITAL(36, 500), CREAM)
    base = H - 150 - off
    place_dish(bg, os.path.join(SRC, dishes[0]), (120, y + 60, W-120, base), fill=0.42)
    d = ImageDraw.Draw(bg, "RGBA")
    footer(d, W, H, 78 if not story else 200)
    if not story:
        d.text((W-56-150, H-80), "SWIPE  →", font=SANS(19, 600), fill=GOLD)
    return bg

def text_slide(title, lines, W=1080, H=1350, story=False, cta=None):
    bg = background(W, H); d = ImageDraw.Draw(bg, "RGBA")
    frame(d, W, H)
    lg = logo_img(170)
    content_h = lg.height + 50 + 40 + 86*len(title.split("\n")) + 30 + 130*len(lines) + (84 if cta else 0)
    top = int((H - content_h) / 2) - 20
    bg.paste(lg, ((W-lg.width)//2, top), lg); d = ImageDraw.Draw(bg, "RGBA")
    y = top + lg.height + 50
    ornament(d, W/2, y); y += 40
    for line in title.split("\n"):
        ctext(d, W/2, y, line, SERIF(80, 600), GOLD); y += 86
    y += 30
    for a, b in lines:
        ctext(d, W/2, y, a.upper(), SANS(24, 600), MUTED, spacing=4); y += 40
        ctext(d, W/2, y, b, SERIF(54, 500), CREAM); y += 90
    if cta:
        y += 10; ornament(d, W/2, y); y += 34
        ctext(d, W/2, y, cta, ITAL(40, 500), GOLD)
    footer(d, W, H, 78 if not story else 230)
    return bg

def save(img, rel):
    p = os.path.join(OUT, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    img.convert("RGB").save(p, "JPEG", quality=92, optimize=True, progressive=True)
    print(p)

DISH = {
 "egg": ("The EPŌS Egg Croissant.png", "The EPŌS Egg Croissant", "Scrambled eggs, gouda, onion jam, arugula", "$12"),
 "bacon": ("Bacon & Egg  Croissant.png", "Bacon & Egg Croissant", "Scrambled eggs, gouda, smoked bacon, arugula", "$13"),
 "salmonc": ("Salmon & Guac Croissant .png", "Salmon & Guac Croissant", "Scrambled eggs, gouda, smoked salmon, guac, arugula", "$16"),
 "borscht": ("Borscht .PNG", "Borscht", "Slow-cooked, served with a warm garlic bun", "$11"),
 "mush": ("Creamy Mushroom soup.PNG", "Creamy Mushroom Velouté", "Silky, earthy, with fresh bread", "$9"),
 "chicken": ("Chicken & Barley Comfort Bowl.PNG", "Chicken & Barley Bowl", "The comfort bowl for a cold day", "$7"),
 "shak": ("Mediterranean Shakshuka.png", "Mediterranean Shakshuka", "Tomato, pepper, eggs, feta, cumin, chili", "$14"),
 "scramble": ("EPŌS Scramble.png", "EPŌS Scramble", "Sourdough, soft scramble, gouda, onion jam", "$13"),
 "toffee": ("Sticky Toffie .png", "Sticky Toffee", "Warm, with vanilla ice cream", "$11"),
 "crumble": ("Apple Crumble.png", "Apple Crumble", "Baked to order, with ice cream", "$12"),
 "salmonb": ("Salmon Begal.png", "Smoked Salmon & Herb Bagel", "Cream cheese, guac, capers, marinated onion", "$14"),
 "turkeyb": ("Turkey & Gouda Bagel .png", "Turkey & Gouda Bagel", "Turkey, gouda, arugula, guac, cream cheese", "$13"),
 "pesto": ("Pesto & Roasted Veggie Bagel.png", "Pesto & Roasted Veggie Bagel", "Roasted veg, pesto, arugula, cream cheese", "$13"),
 "pastrami": ("Pastrami & Gouda Melt.png", "Pastrami & Gouda Melt", "Pastrami, gouda, dill pickles, yellow mustard", "$16"),
 "turkey": ("Turkey & Gouda .png", "Turkey & Gouda Sub", "Turkey, gouda, arugula, pesto, burger sauce", "$14"),
 "medveg": ("Mediterranean Veggie.png", "Mediterranean Veggie", "Roasted veg, arugula, feta, pesto", "$14"),
 "lorraine": ("Classic Lorraine.PNG", "Quiche Lorraine", "Classic, baked in-house", "$10"),
 "wildm": ("Wild Mushroom & Thyme.PNG", "Wild Mushroom & Thyme Quiche", "Baked in-house", "$12"),
 "spinach": ("Spinach & Feta (Mediterranean).png", "Spinach & Feta Quiche", "Baked in-house", "$11"),
 "smq": ("Smoked Salmon.png", "Smoked Salmon Quiche", "Baked in-house", "$13"),
}
def ds(k, **kw):
    a = DISH[k]; return dish_slide(a[0], a[1], a[2], a[3], **kw)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    P1 = "2026-11-29 w0a Meet the kitchen/"
    if which in ("all", "p1"):
        save(cover("Made here,\nevery morning", "Real food on Gerrard Street", [DISH["egg"][0]]), P1 + "01.jpg")
        for i, k in enumerate(["egg", "salmonb", "borscht", "shak", "pastrami", "toffee"], 2):
            save(ds(k), P1 + f"{i:02d}.jpg")
        save(text_slide("Come hungry", [("Monday – Friday", "8:00 – 5:00"), ("Saturday", "9:00 – 5:00"), ("Sunday", "9:30 – 5:00")], cta="290 Gerrard St E"), P1 + "08.jpg")
    P2 = "2026-11-25 w0b Soup season/"
    if which in ("all", "p2"):
        save(cover("Soup season", "Three bowls for a cold Toronto day", [DISH["borscht"][0], DISH["mush"][0], DISH["chicken"][0]]), P2 + "01.jpg")
        for i, k in enumerate(["borscht", "mush", "chicken"], 2): save(ds(k), P2 + f"{i:02d}.jpg")
    P3 = "2026-11-27 w0c Croissant sandwiches/"
    if which in ("all", "p3"):
        save(cover("The croissant\nsandwiches", "Flaky, buttery, built to order", [DISH["salmonc"][0]]), P3 + "01.jpg")
        for i, k in enumerate(["egg", "bacon", "salmonc"], 2): save(ds(k), P3 + f"{i:02d}.jpg")
    P4 = "2026-11-28 w0d Weekend brunch/"
    if which in ("all", "p4"):
        save(cover("Weekend brunch", "Saturday from 9 · Sunday from 9:30", [DISH["shak"][0], DISH["scramble"][0], DISH["crumble"][0]]), P4 + "01.jpg")
        for i, k in enumerate(["shak", "scramble", "crumble", "toffee"], 2): save(ds(k), P4 + f"{i:02d}.jpg")
    PS = "Stories 2026-11-23 to 11-29/"
    if which in ("all", "stories"):
        days = [("Mon", "egg"), ("Tue", "borscht"), ("Wed", "salmonb"), ("Thu", "pastrami"), ("Fri", "lorraine"), ("Sat", "shak"), ("Sun", "toffee")]
        for i, (dname, k) in enumerate(days, 1):
            save(ds(k, W=1080, H=1920, kicker="Today at EPŌS", story=True), PS + f"{i}-{dname}-dish.jpg")
        save(text_slide("We're open", [("Monday – Friday", "8:00 – 5:00"), ("Saturday", "9:00 – 5:00"), ("Sunday", "9:30 – 5:00")], W=1080, H=1920, story=True, cta="Coffee · Pastry · Food · Cakes"), PS + "hours.jpg")

    SP = "/mnt/user-data/uploads/Movies/EPOS Instagram/1 Raw/Stories and extra/"
    order = [("Monday","Egg"),("Tuesday","Bagel"),("Wednesday","Panini"),("Thursday","Quiche"),("Friday","Croissant"),("Saturday","Brunch"),("Sunday","Sweet")]
    if which in ("all","specials"):
        for i,(day,k) in enumerate(order,1):
            im = Image.open(SP+f"EPOS_{k}_{day}.png").convert("RGB")
            c = im.crop((0,408,1080,1758))
            save(c, f"2026-11-23 w0s Daily specials/{i:02d}-{day}.jpg")
            save(im, f"Stories 2026-11-23 to 11-29/special-{i}-{day}.jpg")
