#!/usr/bin/env python3
"""TikTok version of a YouTube Short: drop the "link on our channel" CTA scene, add a "Link in bio" end card.

  python3 tools/tiktok_short.py <slug> <pick_number> <out.mp4>

Needs v/<slug>.mp4, jobs/<slug>/durations.json and pins/<slug>.jpg.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
BG, LIME, GREY = (15, 18, 22), (205, 240, 60), (170, 178, 190)
FB = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
END = 3.5

slug, pick, out = sys.argv[1], sys.argv[2], sys.argv[3]
src = os.path.join(ROOT, "v", f"{slug}.mp4")
durs = json.load(open(os.path.join(ROOT, "jobs", slug, "durations.json")))
cut = sum(durs[:-1]) + 0.25
tmp = tempfile.mkdtemp()

# end card
pin = Image.open(os.path.join(ROOT, "pins", f"{slug}.jpg")).convert("RGB")
card = Image.new("RGB", (W, H), BG)
fg = pin.resize((760, int(760 * pin.height / pin.width)))
card.paste(fg, ((W - fg.width) // 2, 230))
d = ImageDraw.Draw(card)
y = 230 + fg.height + 70
f1, f2, f3 = ImageFont.truetype(FB, 92), ImageFont.truetype(FB, 54), ImageFont.truetype(FB, 40)
t = "LINK IN BIO"
tw = d.textlength(t, font=f1)
d.rounded_rectangle([(W - tw) / 2 - 50, y, (W + tw) / 2 + 50, y + 150], 75, fill=LIME)
d.text(((W - tw) / 2, y + 18), t, font=f1, fill=BG)
t2 = f"Pick #{pick} · full review + link"
d.text(((W - d.textlength(t2, font=f2)) / 2, y + 190), t2, font=f2, fill=(255, 255, 255))
t3 = "yaypicks.com"
d.text(((W - d.textlength(t3, font=f3)) / 2, y + 270), t3, font=f3, fill=GREY)
cardp = os.path.join(tmp, "end.png")
card.save(cardp)
if "--still" in sys.argv:
    card.save(out.replace(".mp4", "-end.jpg")); sys.exit()

run = lambda *a: subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *a], check=True)
a = os.path.join(tmp, "a.mp4"); b = os.path.join(tmp, "b.mp4")
run("-i", src, "-t", f"{cut:.2f}", "-vf", f"scale={W}:{H},fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20",
    "-c:a", "aac", "-ar", "44100", "-ac", "2", a)
run("-loop", "1", "-i", cardp, "-stream_loop", "-1", "-i", os.path.join(ROOT, "assets", "music.wav"),
    "-t", str(END), "-vf", "fps=30,format=yuv420p", "-af", f"volume=0.35,afade=t=in:d=0.3,afade=t=out:st={END-0.8}:d=0.8",
    "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-ar", "44100", "-ac", "2", b)
run("-i", a, "-i", b, "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]", "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-crf", "21", "-c:a", "aac", "-movflags", "+faststart", out)
print(out, f"{cut+END:.1f}s", os.path.getsize(out) // 1024, "KB")
