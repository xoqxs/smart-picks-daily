#!/usr/bin/env python3
"""Weekly 16:9 roundup video from several Short jobs.

Usage:
  python3 tools/build_long.py <out-slug> "<Title shown in intro>" jobs/<a> jobs/<b> ... [--stills]

Each job folder must already contain video.json, durations.json and vo/l*.wav (made by build.py).
Writes v/<out-slug>.mp4 and v/<out-slug>-chapters.txt (YouTube chapters, first line 0:00).
Narration per product = that Short's lines minus its final CTA line, plus a generated intro and outro line.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import XB, MD, BG, CARD, LIME, WHITE, GREY, ease, ease_io, prog, mix, wrap, KOKORO, VOICE, ROOT

W, H, FPS = 1920, 1080, 30
CW, CH = 1000, 850
CX, CY = 90, 140


def fmt(t):
    t = int(t); return f"{t//60}:{t%60:02d}"


class Seg:  # one narrated scene
    def __init__(self, kind, line, wav, dur, job=None, sc=None, imgs=None, cfg=None, idx=0, n=0, title=""):
        self.kind, self.line, self.wav, self.dur = kind, line, wav, dur
        self.job, self.sc, self.imgs, self.cfg, self.idx, self.n, self.title = job, sc, imgs, cfg, idx, n, title


def tts(text, path):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    a, sr = Kokoro(*KOKORO).create(text, voice=VOICE, speed=1.05, lang="en-us")
    sf.write(path, a, sr); return len(a) / sr


def build(out_slug, title, jobs, stills=False):
    work = os.path.join(ROOT, "jobs", out_slug); os.makedirs(work, exist_ok=True)
    segs = []
    intro = f"{title}. Here are this week's {len(jobs)} smart picks, with the specs that matter and the catch for each one."
    segs.append(Seg("intro", intro, os.path.join(work, "intro.wav"), 0, title=title, n=len(jobs)))
    chapters = []
    for j, job in enumerate(jobs):
        cfg = json.load(open(os.path.join(job, "video.json")))
        dur = json.load(open(os.path.join(job, "durations.json")))
        imgs = {k: Image.open(os.path.join(job, p)).convert("RGB") for k, p in cfg["images"].items()}
        scs = cfg["scenes"]
        body = [i for i, s in enumerate(scs) if s.get("type") != "cta"]
        for k, i in enumerate(body):
            segs.append(Seg(scs[i].get("type", "card"), scs[i]["line"], os.path.join(job, "vo", f"l{i+1}.wav"),
                            dur[i], job, scs[i], imgs, cfg, j + 1, len(jobs), cfg.get("name", "")))
            if k == 0: segs[-1].first = True
    outro = "Every link is in the description, and all picks are on our Video Picks page. Which one would you buy? Tell us in the comments."
    segs.append(Seg("outro", outro, os.path.join(work, "outro.wav"), 0))
    for s in (segs[0], segs[-1]):
        s.dur = (tts(s.line, s.wav) if not stills else 4.0) + 0.6
    t = 0.0
    for s in segs:
        if getattr(s, "first", False): chapters.append((t, f"#{s.idx} {s.cfg.get('name', s.cfg['slug'])}"))
        s.start = t; t += s.dur
    total = t

    def frame(s, tt):
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        d.rounded_rectangle([90, 60, W - 90, 66], 3, fill=(40, 46, 58))
        d.rounded_rectangle([90, 60, 90 + (W - 180) * min(1, (s.start + tt) / total), 66], 3, fill=LIME)
        d.text((90, 84), "SMART PICKS DAILY", font=XB(30), fill=GREY)
        d.text((W - 90 - d.textlength("#ad", font=XB(30)), 84), "#ad", font=XB(30), fill=GREY)
        if s.kind == "intro":
            a = prog(tt, 0.1, 0.5)
            for i, ln in enumerate(wrap(d, s.title, XB(110), W - 300)):
                d.text((150, 330 + i * 130 + (1 - a) * 30), ln, font=XB(110), fill=mix(WHITE, a))
            d.text((150, 700), f"{s.n} picks · specs · the catch", font=MD(52), fill=mix(LIME, prog(tt, 0.8, 0.5)))
            return im
        if s.kind == "outro":
            a = prog(tt, 0.1, 0.5)
            d.text((150, 360), "Links in the description", font=XB(96), fill=mix(WHITE, a))
            d.text((150, 500), "All picks: Video Picks page on our channel", font=MD(52), fill=mix(LIME, prog(tt, 0.6, 0.5)))
            d.text((150, 600), "As an Amazon Associate we earn from qualifying purchases.", font=MD(36), fill=mix(GREY, a))
            return im
        sc = s.sc
        if s.kind == "card" or s.kind == "cta":
            src = s.imgs[sc["image"]]; a_, b_ = sc["from"], sc.get("to", sc["from"])
            k = ease_io(tt / s.dur)
            cx = a_[0] + (b_[0] - a_[0]) * k; cy = a_[1] + (b_[1] - a_[1]) * k; w = a_[2] + (b_[2] - a_[2]) * k
            h = w * CH / CW
            crop = src.crop(tuple(int(v) for v in (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))).resize((CW, CH), Image.LANCZOS)
            m = Image.new("L", (CW, CH), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, CW, CH], 40, fill=255)
            im.paste(crop, (CX, CY), m); d = ImageDraw.Draw(im)
            cr = s.cfg.get("credit", "")
            if cr: d.text((CX + CW - d.textlength(cr, font=MD(24)) - 22, CY + CH - 40), cr, font=MD(24), fill=(120, 125, 135))
            bd = sc.get("badge")
            if bd:
                a = prog(tt, 0.5, 0.4)
                if a > 0:
                    d.rounded_rectangle([CX + 28, CY + 28, CX + 28 + d.textlength(bd["big"], font=XB(110)) + 56, CY + 180], 32, fill=mix(BG, a, (255, 255, 255)))
                    d.text((CX + 56, CY + 36), bd["big"], font=XB(110), fill=mix(LIME, a, (255, 255, 255)))
        else:  # tip
            boxes = sc["boxes"][:3]
            for k, (ti, su) in enumerate(boxes):
                ia = prog(tt, 0.4 + k * 0.5, 0.4); x = CX + 20 + k * 330; y = CY + 260
                d.rounded_rectangle([x, y, x + 300, y + 260], 32, fill=mix(CARD, ia), outline=mix(LIME, ia), width=5)
                d.text((x + (300 - d.textlength(ti, font=XB(72))) / 2, y + 50), ti, font=XB(72), fill=mix(LIME, ia))
                d.text((x + (300 - d.textlength(su, font=MD(34))) / 2, y + 150), su, font=MD(34), fill=mix(GREY, ia))
        # right column: product number + name + narration line
        rx = CX + CW + 80; rw = W - rx - 90
        d.text((rx, 170), f"PICK {s.idx} OF {s.n}", font=XB(34), fill=LIME)
        y = 230
        for ln in wrap(d, s.cfg.get("name", ""), XB(60), rw):
            d.text((rx, y), ln, font=XB(60), fill=WHITE); y += 72
        a = prog(tt, 0.05, 0.3); y += 40
        for ln in wrap(d, s.line, MD(46), rw):
            x = rx
            for w_ in ln.split(" "):
                col = LIME if any(h.lower() in w_.lower() for h in sc.get("hl", [])) else WHITE
                d.text((x, y + (1 - a) * 16), w_, font=MD(46), fill=mix(col, a)); x += d.textlength(w_ + " ", font=MD(46))
            y += 60
        return im

    out = os.path.join(work, "out"); os.makedirs(out, exist_ok=True)
    if stills:
        for i, s in enumerate(segs): frame(s, s.dur * 0.8).save(f"{out}/still{i+1}.png")
        print("stills in", out); return
    with open(os.path.join(out, "list.txt"), "w") as fh:
        for i, s in enumerate(segs):
            tmp, fin = f"{out}/s{i+1}.tmp.mp4", f"{out}/s{i+1}.mp4"
            p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                                  "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                                  "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
            for k in range(int(round(s.dur * FPS))): p.stdin.write(frame(s, k / FPS).tobytes())
            p.stdin.close()
            if p.wait() != 0: raise SystemExit("ffmpeg failed")
            os.replace(tmp, fin); fh.write(f"file 's{i+1}.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", f"{out}/list.txt", "-c", "copy", f"{out}/video.mp4"], check=True)
    args = ["ffmpeg", "-y", "-loglevel", "error"]
    for s in segs: args += ["-i", s.wav]
    args += ["-stream_loop", "-1", "-i", os.path.join(ROOT, "assets", "music.wav")]
    n = len(segs)
    fc = "".join(f"[{i}:a]aresample=44100,adelay={int(s.start*1000+250)}|{int(s.start*1000+250)}[v{i}];" for i, s in enumerate(segs))
    fc += "".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0[vo];[{n}:a]volume=0.10[m];[vo][m]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5[o]"
    subprocess.run(args + ["-filter_complex", fc, "-map", "[o]", "-ar", "44100", "-t", f"{total:.2f}", f"{out}/audio.m4a"], check=True)
    final = os.path.join(ROOT, "v", out_slug + ".mp4"); os.makedirs(os.path.dirname(final), exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{out}/video.mp4", "-i", f"{out}/audio.m4a", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", final], check=True)
    with open(os.path.join(ROOT, "v", out_slug + "-chapters.txt"), "w") as fh:
        fh.write("0:00 Intro\n"); [fh.write(f"{fmt(t)} {name}\n") for t, name in chapters]
        fh.write(f"{fmt(segs[-1].start)} Wrap-up\n")
    print(final, f"{total:.1f}s")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--stills"]
    build(a[0], a[1], a[2:], stills="--stills" in sys.argv)
