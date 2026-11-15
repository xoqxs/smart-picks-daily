#!/usr/bin/env python3
"""1000x1500 Pinterest pin from jobs/<slug>/video.json "pin" block.

"pin": {"image": "kv", "crop": [cx, cy, size],          # square crop in source pixels
        "headline": "This tiny charger powers a MacBook Air",
        "sub": "iPhone · iPad · MacBook Air · Thermal Guard",  # one short line
        "badge": {"text": "65W", "xy": [690, 600]}}            # optional, xy in pin pixels (image area is x 50-950, y 330-1230)
Writes pins/<slug>.jpg. Check the result with Read before pushing.
"""
import json, os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import XB, MD, BG, LIME, WHITE, wrap, ROOT

GREY = (160, 168, 180)
job = sys.argv[1]
cfg = json.load(open(os.path.join(job, "video.json"))); p = cfg["pin"]
src = Image.open(os.path.join(job, cfg["images"][p["image"]])).convert("RGB")
im = Image.new("RGB", (1000, 1500), BG); d = ImageDraw.Draw(im)
cx, cy, s = p["crop"]
crop = src.crop((cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)).resize((900, 900), Image.LANCZOS)
m = Image.new("L", (900, 900), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 899, 899), radius=48, fill=255)
im.paste(crop, (50, 330), m)
d.text((60, 70), "SMART PICKS DAILY", font=XB(34), fill=GREY)
y = 130
for ln in wrap(d, p["headline"], XB(72), 880)[:2]:
    d.text((60, y), ln, font=XB(72), fill=WHITE); y += 84
b = p.get("badge")
if b:
    x, yy = b["xy"]; tw = d.textlength(b["text"], font=XB(78))
    d.rounded_rectangle((x, yy, x + tw + 56, yy + 100), radius=24, fill=BG)
    d.polygon([(x, yy + 30), (x - 30, yy + 10), (x, yy + 60)], fill=BG)
    d.text((x + 28, yy + 8), b["text"], font=XB(78), fill=LIME)
name = cfg.get("name", "")
f = XB(46)
while d.textlength(name, font=f) > 880 and f.size > 30: f = XB(f.size - 2)
d.text((60, 1260), name, font=f, fill=WHITE)
d.text((60, 1320), p.get("sub", ""), font=MD(32), fill=GREY)
d.rounded_rectangle((60, 1385, 520, 1455), radius=35, fill=LIME)
d.text((90, 1398), "See specs & price →", font=XB(36), fill=BG)
cr = cfg.get("credit", "")
d.text((940, 1240), cr, font=MD(20), fill=GREY, anchor="ra")
os.makedirs(os.path.join(ROOT, "pins"), exist_ok=True)
out = os.path.join(ROOT, "pins", cfg["slug"] + ".jpg"); im.save(out, quality=90); print(out)
