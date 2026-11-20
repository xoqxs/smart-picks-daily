"""YayPicks brand assets (logo option A: dark rounded square + lime smile)."""
from PIL import Image, ImageDraw, ImageFont
import os
OUT=os.path.dirname(os.path.abspath(__file__))
F="/usr/share/fonts/opentype/inter/"
XB=lambda s: ImageFont.truetype(F+"Inter-ExtraBold.otf", s)
MD=lambda s: ImageFont.truetype(F+"Inter-Medium.otf", s)
DARK=(29,29,31); TILE2=(58,58,60); LIME=(182,227,36); WHITE=(255,255,255); GREY=(160,160,166)

def smile(d, x0, y0, size, width_frac=11/96):
    s=size/96.0; w=max(2,int(round(width_frac*96*s)))
    p0=(x0+27*s,y0+52*s); c=(x0+48*s,y0+76*s); p2=(x0+69*s,y0+52*s)
    n=400
    for i in range(n+1):
        t=i/n
        x=(1-t)**2*p0[0]+2*(1-t)*t*c[0]+t*t*p2[0]
        y=(1-t)**2*p0[1]+2*(1-t)*t*c[1]+t*t*p2[1]
        d.ellipse((x-w/2,y-w/2,x+w/2,y+w/2), fill=LIME)

def tile(size, fill=DARK, sw=11/96, transparent=True):
    S=size*4
    im=Image.new('RGBA',(S,S),(0,0,0,0) if transparent else DARK+(255,)); d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,S-1,S-1), radius=int(S*24/96), fill=fill)
    smile(d,0,0,S,sw)
    return im.resize((size,size),Image.LANCZOS)

tile(1024).save(f'{OUT}/yaypicks-mark-1024.png')
tile(180).save(f'{OUT}/yaypicks-apple-touch-180.png')
tile(48, sw=13/96).save(f'{OUT}/yaypicks-favicon-48.png')

# Avatar 800x800 (platforms crop to a circle): full dark field, big smile
S=3200; a=Image.new('RGB',(S,S),DARK); d=ImageDraw.Draw(a)
smile(d, S*0.14, S*0.10, S*0.72, 12/96)
a=a.resize((800,800),Image.LANCZOS); a.save(f'{OUT}/yaypicks-avatar-800.png')

def wordmark(d, x, y, size, color):
    f=XB(size); d.text((x,y),"YayPicks",font=f,fill=color)
    return d.textlength("YayPicks",font=f)

# YouTube banner 2560x1440 (safe area 1546x423 centered)
b=Image.new('RGB',(2560,1440),DARK); d=ImageDraw.Draw(b)
cx,cy=1280,720; ms=200
fw=XB(150); tw=d.textlength("YayPicks",font=fw)
total=ms+44+tw; x0=cx-total/2
b.paste(tile(ms,fill=TILE2), (int(x0), int(cy-150)), tile(ms,fill=TILE2))
d.text((x0+ms+44, cy-150+18),"YayPicks",font=fw,fill=WHITE)
t1="Honest picks from every Amazon category"; f1=MD(52)
d.text((cx-d.textlength(t1,font=f1)/2, cy+85),t1,font=f1,fill=GREY)
t2="New Shorts every day  ·  yaypicks.com"; f2=MD(40)
d.text((cx-d.textlength(t2,font=f2)/2, cy+160),t2,font=f2,fill=LIME)
b.save(f'{OUT}/yaypicks-youtube-banner.png')

# Wordmark lockups (transparent) for docs/overlays
for name,col in (("light",DARK),("dark",WHITE)):
    W,H=1400,320; im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    im.paste(tile(240), (20,40), tile(240)); wordmark(d, 300, 62, 170, col)
    im.save(f'{OUT}/yaypicks-wordmark-on-{name}.png')
print("ok")
