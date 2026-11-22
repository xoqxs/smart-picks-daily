#!/usr/bin/env python3
"""YayPicks - build one vertical Short from jobs/<slug>/video.json.

Usage:
  python3 tools/build.py jobs/<slug>            # voice + render + mix -> v/<slug>.mp4
  python3 tools/build.py jobs/<slug> --stills   # only save one still per scene (check before full render)

video.json (all text in English):
{
  "slug": "2026-11-15-ugreen-nexode-air-65w",
  "pick": 1,
  "credit": "Image: UGREEN",                    # shown on every image card
  "images": {"kv": "img/kv.jpg"},              # paths relative to the job folder
  "scenes": [
    {"type": "card", "image": "kv", "from": [cx, cy, w], "to": [cx, cy, w],
     "line": "Voice-over sentence.", "hl": ["words", "to", "highlight"],
     "badge": {"big": "65W", "small": "launch price"},   # optional, top-left of card
     "chips": ["iPhone", "iPad"]},                         # optional, appear one by one
    {"type": "tip", "title": "PRO TIP", "boxes": [["65W","charger"],["100W","USB-C cable"],["65W","to laptop"]],
     "note": "Short grey note under the boxes.", "line": "...", "hl": []},
    {"type": "cta", "image": "kv", "from": [...], "to": [...], "line": "...", "hl": []}
  ]
}
from/to = crop window in source pixels: centre x, centre y, width (height follows the 960x820 card ratio).
The last scene should be type "cta": it shows "Pick #N" and "Link on our channel".
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BG = (14, 17, 22); CARD = (26, 31, 40)
LIME = (198, 244, 50); WHITE = (245, 247, 250); GREY = (140, 150, 165)
F = "/usr/share/fonts/opentype/inter/"
XB = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
MD = lambda s: ImageFont.truetype(F + "InterDisplay-Medium.otf", s)
CW, CH = 960, 820
CX, CY = (W - CW) // 2, 250
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KOKORO = ("/tmp/kokoro/kokoro-v1.0.onnx", "/tmp/kokoro/voices-v1.0.bin")
VOICE = "af_heart"   # chosen by the owner on 15 Nov 2026 (female voice "B")


def ease(x):
    x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_io(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def prog(t, s, d): return ease((t - s) / d)
def mix(c, a, base=BG): return tuple(int(base[i] + (c[i] - base[i]) * a) for i in range(3))


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        tst = (cur + " " + w_).strip()
        if d.textlength(tst, font=f) <= maxw: cur = tst
        else: lines.append(cur); cur = w_
    lines.append(cur); return lines


class Video:
    def __init__(self, job):
        self.job = job
        self.cfg = json.load(open(os.path.join(job, "video.json")))
        self.imgs = {k: Image.open(os.path.join(job, p)).convert("RGB") for k, p in self.cfg["images"].items()}
        self.scenes = self.cfg["scenes"]
        self.dur = [3.0] * len(self.scenes)

    # --- drawing helpers ---
    def card(self, im, sc, t, dur):
        src = self.imgs[sc["image"]]
        a, b = sc["from"], sc.get("to", sc["from"])
        k = ease_io(t / dur)
        cx = a[0] + (b[0] - a[0]) * k; cy = a[1] + (b[1] - a[1]) * k; w = a[2] + (b[2] - a[2]) * k
        h = w * CH / CW
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        crop = src.crop(tuple(int(v) for v in box)).resize((CW, CH), Image.LANCZOS)
        mask = Image.new("L", (CW, CH), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, CW, CH], 44, fill=255)
        im.paste(crop, (CX, CY), mask)
        d = ImageDraw.Draw(im); f = MD(26); s = self.cfg.get("credit", "")
        if s:
            d.text((CX + CW - d.textlength(s, font=f) - 24, CY + CH - 44), s, font=f, fill=(120, 125, 135))

    def subtitle(self, d, t, text, hl):
        a = prog(t, 0.05, 0.3); f = XB(64)
        lines = wrap(d, text, f, W - 140)
        y0 = 1560 - (len(lines) - 1) * 40
        for i, ln in enumerate(lines):
            x = (W - d.textlength(ln, font=f)) / 2
            for w_ in ln.split(" "):
                col = LIME if any(h.lower() in w_.lower() for h in hl) else WHITE
                d.text((x, y0 + i * 82 + (1 - a) * 20), w_, font=f, fill=mix(col, a))
                x += d.textlength(w_ + " ", font=f)

    def chip(self, d, x, y, s, a, size=44):
        f = XB(size); tw = d.textlength(s, font=f)
        d.rounded_rectangle([x, y, x + tw + 56, y + size + 40], (size + 40) // 2, fill=mix(LIME, a))
        d.text((x + 28, y + 18), s, font=f, fill=BG if a > 0.5 else mix(LIME, a))
        return tw + 56

    def base(self, i, t):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        total = sum(self.dur); done = sum(self.dur[:i]) + t
        d.rounded_rectangle([60, 120, W - 60, 128], 4, fill=(40, 46, 58))
        d.rounded_rectangle([60, 120, 60 + (W - 120) * min(1, done / total), 128], 4, fill=LIME)
        f = XB(40); d.text((60, 160), "YAYPICKS.COM", font=f, fill=GREY)
        s = "#ad"; d.text((W - 60 - d.textlength(s, font=f), 160), s, font=f, fill=GREY)
        return im

    def frame(self, i, t):
        sc, dur = self.scenes[i], self.dur[i]
        im = self.base(i, t)
        typ = sc.get("type", "card")
        if typ in ("card", "cta"):
            self.card(im, sc, t, dur)
        d = ImageDraw.Draw(im)
        if typ == "card":
            bd = sc.get("badge")
            if bd:
                a = prog(t, 0.6, 0.4)
                if a > 0:
                    f = XB(130); tw = d.textlength(bd["big"], font=f)
                    hgt = 200 if bd.get("small") else 160
                    d.rounded_rectangle([CX + 30, CY + 30, CX + 30 + max(tw, 260) + 60, CY + 30 + hgt], 36, fill=mix(BG, a, (255, 255, 255)))
                    d.text((CX + 60, CY + 38), bd["big"], font=f, fill=mix(LIME, a, (255, 255, 255)))
                    if bd.get("small"):
                        d.text((CX + 62, CY + 180), bd["small"], font=MD(34), fill=mix(GREY, a, (255, 255, 255)))
            chips = sc.get("chips", [])
            x = CX + 30
            for k, s in enumerate(chips):
                a = prog(t, 1.0 + k * 0.5, 0.35)
                if a > 0:
                    x += self.chip(d, x, CY + CH - 130, s, a) + 16
        elif typ == "tip":
            a = prog(t, 0.1, 0.4); s = sc.get("title", "PRO TIP"); f = XB(48)
            self.chip(d, (W - d.textlength(s, font=f) - 56) / 2, 330, s, a, size=48)
            boxes = sc["boxes"][:3]; n = len(boxes)
            bw = 280 if n == 3 else 420
            gap = (W - 2 * 70 - n * bw) / max(1, n - 1) if n > 1 else 0
            xs = [70 + k * (bw + gap) for k in range(n)] if n > 1 else [(W - bw) / 2]
            for k, (ti, su) in enumerate(boxes):
                ia = prog(t, 0.6 + k * 0.6, 0.4); col = WHITE if k == 0 and n == 3 else LIME
                y = 560 + (1 - ia) * 40
                d.rounded_rectangle([xs[k], y, xs[k] + bw, y + 260], 36, fill=mix(CARD, ia), outline=mix(col, ia), width=6)
                f1, f2 = XB(76), MD(36)
                tw = d.textlength(ti, font=f1); d.text((xs[k] + (bw - tw) / 2, y + 52), ti, font=f1, fill=mix(col, ia))
                sw = d.textlength(su, font=f2); d.text((xs[k] + (bw - sw) / 2, y + 152), su, font=f2, fill=mix(GREY, ia))
            if sc.get("note"):
                a = prog(t, 2.4, 0.4)
                if a > 0:
                    f = MD(42)
                    for j, ln in enumerate(wrap(d, sc["note"], f, W - 160)):
                        d.text(((W - d.textlength(ln, font=f)) / 2, 920 + j * 56), ln, font=f, fill=mix(GREY, a))
        elif typ == "cta":
            a = prog(t, 0.3, 0.4)
            if a > 0:
                s = f"Pick #{self.cfg['pick']}"; f = XB(110); tw = d.textlength(s, font=f)
                d.rounded_rectangle([CX + 30, CY + 30, CX + 30 + tw + 60, CY + 190], 36, fill=mix(BG, a, (255, 255, 255)))
                d.text((CX + 60, CY + 42), s, font=f, fill=mix(LIME, a, (255, 255, 255)))
            a = prog(t, 1.2, 0.4)
            if a > 0:
                bob = math.sin(t * 6) * 10
                f = XB(58); s = "Link on our channel"
                d.text(((W - d.textlength(s, font=f)) / 2, 1110 + bob), s, font=f, fill=mix(LIME, a))
                f2 = MD(40); s2 = "Tap the channel name  ·  Video Picks"
                d.text(((W - d.textlength(s2, font=f2)) / 2, 1190 + bob), s2, font=f2, fill=mix(GREY, a))
                f3 = XB(44); s3 = "or search it on yaypicks.com"
                d.text(((W - d.textlength(s3, font=f3)) / 2, 1258 + bob), s3, font=f3, fill=mix(WHITE, a))
        self.subtitle(d, t, sc["line"], sc.get("hl", []))
        return im

    # --- pipeline ---
    def voice(self):
        import soundfile as sf
        from kokoro_onnx import Kokoro
        k = Kokoro(*KOKORO)
        vd = os.path.join(self.job, "vo"); os.makedirs(vd, exist_ok=True)
        lens = []
        for i, sc in enumerate(self.scenes):
            a, sr = k.create(sc["line"], voice=VOICE, speed=1.05, lang="en-us")
            sf.write(os.path.join(vd, f"l{i+1}.wav"), a, sr); lens.append(len(a) / sr)
        self.dur = [x + 0.5 for x in lens]; self.dur[-1] += 0.8
        json.dump(self.dur, open(os.path.join(self.job, "durations.json"), "w"))

    def load_durations(self):
        p = os.path.join(self.job, "durations.json")
        if os.path.exists(p): self.dur = json.load(open(p))

    def render(self):
        out = os.path.join(self.job, "out"); os.makedirs(out, exist_ok=True)
        with open(os.path.join(out, "list.txt"), "w") as fh:
            for i in range(len(self.scenes)):
                tmp, final = f"{out}/s{i+1}.tmp.mp4", f"{out}/s{i+1}.mp4"
                p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                      "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                                      "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
                for k in range(int(round(self.dur[i] * FPS))):
                    p.stdin.write(self.frame(i, k / FPS).tobytes())
                p.stdin.close()
                if p.wait() != 0: raise SystemExit(f"ffmpeg failed on scene {i+1}")
                os.replace(tmp, final); fh.write(f"file 's{i+1}.mp4'\n")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                        os.path.join(out, "list.txt"), "-c", "copy", os.path.join(out, "video.mp4")], check=True)

    def mix(self):
        n = len(self.scenes); total = sum(self.dur)
        starts = [sum(self.dur[:i]) for i in range(n)]
        args = ["ffmpeg", "-y", "-loglevel", "error"]
        for i in range(n): args += ["-i", os.path.join(self.job, "vo", f"l{i+1}.wav")]
        args += ["-stream_loop", "-1", "-i", os.path.join(ROOT, "assets", "music.wav")]
        fc = "".join(f"[{i}:a]aresample=44100,adelay={int(s*1000+250)}|{int(s*1000+250)}[v{i}];" for i, s in enumerate(starts))
        fc += "".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0[vo];[{n}:a]volume=0.12[m];"
        fc += "[vo][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[out]"
        audio = os.path.join(self.job, "out", "audio.m4a")
        subprocess.run(args + ["-filter_complex", fc, "-map", "[out]", "-ar", "44100", "-t", f"{total:.2f}", audio], check=True)
        os.makedirs(os.path.join(ROOT, "v"), exist_ok=True)
        final = os.path.join(ROOT, "v", self.cfg["slug"] + ".mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(self.job, "out", "video.mp4"), "-i", audio,
                        "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final], check=True)
        return final


if __name__ == "__main__":
    job = sys.argv[1]
    v = Video(job)
    if "--stills" in sys.argv:
        v.load_durations()
        out = os.path.join(job, "out"); os.makedirs(out, exist_ok=True)
        for i in range(len(v.scenes)):
            v.frame(i, v.dur[i] * 0.8).save(f"{out}/still{i+1}.png")
        print("stills saved in", out)
    else:
        v.voice(); v.render(); print(v.mix())
