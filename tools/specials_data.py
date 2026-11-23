# Single source of truth for the daily specials (v3.1 after critic round; current menu prices, no price rises).
# Used by gen/specials3.py (graphics) and site2/build.py (website).
# Window rule: Tue–Thu all day (soup from 11). Fri–Mon until 1. Sunday pudding from noon.
SPECIALS = [
    dict(day="Monday", name="Egg Monday", pair="EPŌS Scramble & a Latte", price="17", save="SAVE $2",
         start="08:00", end="13:00", dishes=["EPŌS Scramble.png"], cups=["latte"], inc="",
         desc="Soft scramble on sourdough with gouda and onion jam, and a 12 oz latte, hot or iced.", img="monday"),
    dict(day="Tuesday", name="Shakshuka Tuesday", pair="Shakshuka, Bread & a Latte", price="17", save="SAVE UP TO $3",
         start="08:00", end="13:00", dishes=["Mediterranean Shakshuka.png"], cups=["latte"], inc="LATTE OR CHAI LATTE",
         desc="Our shakshuka with feta and bread, and a 12 oz latte or chai latte.", img="tuesday"),
    dict(day="Wednesday", name="Soup Wednesday", pair="Any Soup & a Hot Sandwich", price="18", save="SAVE UP TO $5",
         start="08:00", end="13:00", dishes=["Turkey & Gouda .png", "Creamy Mushroom soup.PNG"], cups=[],
         inc="BORSCHT OR PASTRAMI +$2",
         desc="Mushroom velouté or chicken & barley, with a Turkey & Gouda or Mediterranean Veggie hot sandwich. Borscht or pastrami +$2.", img="wednesday"),
    dict(day="Thursday", name="Croissant Thursday", pair="Egg Croissant & a Latte", price="16", save="SAVE $2",
         start="08:00", end="13:00", dishes=["The EPŌS Egg Croissant.png"], cups=["latte"], inc="TWO FOR $30  ·  BACON +$1",
         desc="The EPŌS Egg Croissant and a 12 oz latte. Bring a friend: two for $30. Bacon +$1.", img="thursday"),
    dict(day="Friday", name="Pastrami Friday", pair="Pastrami Melt & an Americano", price="17", save="SAVE $2",
         start="08:00", end="13:00", dishes=["Pastrami & Gouda Melt.png"], cups=["americano"], inc="",
         desc="Pastrami & Gouda Melt with dill pickles and mustard, pressed to order, and an Americano, hot or iced.", img="friday"),
    dict(day="Saturday", name="Brunch Saturday", pair="Salmon & Guac Croissant, with a Latte", price="19", save="SAVE UP TO $3",
         start="09:00", end="13:00", dishes=["Salmon & Guac Croissant .png"], cups=["latte"], inc="LATTE OR CHAI LATTE",
         desc="Scrambled eggs, smoked salmon, guac and gouda in a butter croissant, with a 12 oz latte or chai latte.", img="saturday"),
    dict(day="Sunday", name="Sweet Sunday", pair="Sticky Toffee Pudding & a Latte", price="15", save="SAVE $2",
         start="09:30", end="13:00", dishes=["Sticky Toffie .png"], cups=["latte"], inc="APPLE CRUMBLE INSTEAD +$1",
         desc="Warm sticky toffee pudding with vanilla ice cream, and a 12 oz latte.", img="sunday"),
]
EXTRA = dict(name="Coffee & Cake", days="Tue – Thu", pair="Any Cake & a 12 oz Drink", price="11", save="SAVE UP TO $3",
             start="14:00", end="17:00", inc="LATTE, CHAI, MATCHA OR LONDON FOG",
             cakes="EPŌS Cake  ·  Carrot Cake  ·  Tiramisu  ·  Mint Panna Cotta",
             desc="Any slice of cake with a 12 oz latte, chai, matcha or London Fog. Tuesday to Thursday, 2 to 5.")
RULE = "All daily specials from opening until 1 PM. Coffee & Cake Tue–Thu 2–5."

def nice(t):
    h, m = map(int, t.split(":")); ap = "AM" if h < 12 else "PM"; h12 = h - 12 if h > 12 else h
    return (f"{h12}:{m:02d}" if m else f"{h12}"), ap

def window(s):
    (a, ap1), (b, ap2) = nice(s["start"]), nice(s["end"])
    return f"{a} {ap1} – {b} {ap2}" if ap1 != ap2 else f"{a} – {b} {ap2}"
