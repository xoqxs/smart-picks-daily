#!/usr/bin/env python3
"""Build small search thumbnails + site/search.json (post path -> thumb) for the live site search.
Run after adding picks:  python3 tools/search_index.py   (then commit thumbs/s and site/search.json)."""
import json, os
from urllib.parse import urlparse
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs('thumbs/s', exist_ok=True)
picks = json.load(open('picks.json')); out = {}
for p in picks:
    post, job = p.get('post'), p.get('job')
    if not post or not job: continue
    src = os.path.join(job, 'img', 'kv.jpg')
    if not os.path.exists(src):
        imgs = [f for f in os.listdir(os.path.join(job, 'img'))] if os.path.isdir(os.path.join(job, 'img')) else []
        if not imgs: continue
        src = os.path.join(job, 'img', sorted(imgs)[0])
    slug = os.path.basename(job.rstrip('/'))
    dst = f'thumbs/s/{slug}.jpg'
    if not os.path.exists(dst):
        im = Image.open(src).convert('RGB'); w, h = im.size; s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((160, 160), Image.LANCZOS)
        im.save(dst, quality=82, optimize=True)
    out[urlparse(post).path] = dst
json.dump(out, open('site/search.json', 'w'), separators=(',', ':'))
print(len(out), 'thumbs')
