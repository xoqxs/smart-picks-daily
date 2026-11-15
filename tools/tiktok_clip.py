#!/usr/bin/env python3
"""Turn one or more pin images into a vertical 1080x1920 TikTok clip with music.

  python3 tools/tiktok_clip.py <out.mp4> <img1.jpg> [img2.jpg ...]

Each image is shown ~4.5 s (single image: 9 s) on a blurred background with a slow zoom.
Uses assets/music.wav (same bed as the Shorts) at low volume.
"""
import os, subprocess, sys, tempfile
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30

out, imgs = sys.argv[1], sys.argv[2:]
per = 9.0 if len(imgs) == 1 else 4.5
tmp = tempfile.mkdtemp()
parts = []
for i, p in enumerate(imgs):
    im = Image.open(p).convert("RGB")
    bg = im.resize((W, int(W * im.height / im.width))).crop((0, 0, W, H)) if im.height / im.width >= H / W else im.resize((int(H * im.width / im.height), H))
    bg = bg.resize((W, H)).filter(ImageFilter.GaussianBlur(40))
    fg = im.resize((1000, int(1000 * im.height / im.width)))
    canvas = bg.copy()
    canvas.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    frame = os.path.join(tmp, f"f{i}.png")
    canvas.save(frame)
    seg = os.path.join(tmp, f"s{i}.mp4")
    n = int(per * FPS)
    vf = (f"scale={W*2}:{H*2},zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={n}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", frame, "-vf", vf,
                    "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "20", seg], check=True)
    parts.append(seg)

lst = os.path.join(tmp, "list.txt")
open(lst, "w").write("".join(f"file '{s}'\n" for s in parts))
dur = per * len(imgs)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                "-stream_loop", "-1", "-i", os.path.join(ROOT, "assets", "music.wav"),
                "-filter_complex", f"[1:a]volume=0.35,afade=t=out:st={dur-1.2}:d=1.2[a]",
                "-map", "0:v", "-map", "[a]", "-t", str(dur), "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                "-movflags", "+faststart", out], check=True)
print(out, f"{dur:.1f}s", os.path.getsize(out) // 1024, "KB")
