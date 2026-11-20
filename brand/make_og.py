"""1200x630 Open Graph share cards for yaypicks.com (default, categories, Black Friday)."""
import os, sys
sys.argv=[sys.argv[0]]
from PIL import Image, ImageDraw
here=os.path.dirname(os.path.abspath(__file__))
exec(open(f'{here}/make_yaypicks.py').read().split("tile(1024)")[0])
OUT=os.path.join(here,'..','site','og'); os.makedirs(OUT,exist_ok=True)
def card(name, kicker, title, sub, accent=LIME):
    W,H=1200,630; im=Image.new('RGB',(W,H),DARK); d=ImageDraw.Draw(im)
    ms=96; t=tile(ms,fill=TILE2); im.paste(t,(72,64),t)
    d.text((72+ms+24,78),"YayPicks",font=XB(58),fill=WHITE)
    y=250
    if kicker:
        f=MD(30); w=d.textlength(kicker,font=f)
        d.rounded_rectangle((72,y-6,72+w+40,y+44),radius=25,fill=accent)
        d.text((92,y),kicker,font=f,fill=DARK); y+=78
    fz=74
    while d.textlength(title,font=XB(fz))>1056 and fz>40: fz-=2
    d.text((72,y),title,font=XB(fz),fill=WHITE); y+=fz+26
    d.text((72,y),sub,font=MD(34),fill=GREY)
    d.text((72,H-84),"yaypicks.com",font=MD(32),fill=accent)
    smile(d, W-330, H-330, 300, 11/96)
    im.save(f'{OUT}/{name}.jpg',quality=90)
card('default',None,'Honest Amazon picks','Researched reviews for tech, home & kitchen and beauty')
card('tech','Tech','Tech picks worth buying','Headphones, chargers, desk gear and smart home')
card('home-kitchen','Home & Kitchen','Home & kitchen favorites','Appliances, cookware, coffee gear and home care')
card('beauty','Beauty','Beauty bestsellers, explained','Skincare, hair care and makeup that people rebuy')
card('black-friday','Black Friday Week','Black Friday gift picks','Bestsellers from our reviews, updated daily',accent=(255,92,72))
print(os.listdir(OUT))
