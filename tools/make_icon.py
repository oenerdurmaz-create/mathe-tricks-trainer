#!/usr/bin/env python3
"""Zeichnet das vorlaeufige App-Icon (1024x1024, ohne Transparenz):
Nachtblau, Zeit-Ring (Tuerkis, Rest Koralle) und ein Blitz in der Mitte."""
from PIL import Image, ImageDraw
import math, pathlib
S=4096
img=Image.new('RGB',(S,S),(15,27,61))
d=ImageDraw.Draw(img)
# weicher Verlauf von oben (heller) nach unten
for y in range(S):
    k=y/S
    c=(int(28-13*k),int(45-18*k),int(99-38*k))
    d.line([(0,y),(S,y)],fill=c)
cx=cy=S//2; R=int(S*0.36); W=int(S*0.075)
box=[cx-R,cy-R,cx+R,cy+R]
d.arc(box,0,360,fill=(36,55,111),width=W)               # Spur
d.arc(box,-90,168,fill=(46,196,182),width=W)            # Restzeit tuerkis
d.arc(box,192,232,fill=(255,122,89),width=W)            # Ende koralle
# runde Kappen
def cap(deg,col):
    a=math.radians(deg); r=R-W/2
    x=cx+r*math.cos(a); y=cy+r*math.sin(a)
    d.ellipse([x-W/2,y-W/2,x+W/2,y+W/2],fill=col)
cap(-90,(46,196,182)); cap(168,(46,196,182)); cap(192,(255,122,89)); cap(232,(255,122,89))
# Blitz
u=S/1000
pts=[(560,250),(345,545),(480,545),(430,760),(665,445),(525,445),(600,250)]
pts=[(cx+(x-500)*u*1.0,cy+(y-505)*u*1.0) for x,y in pts]
sh=[(x+40,y+50) for x,y in pts]
d.polygon(sh,fill=(9,16,38))
d.polygon(pts,fill=(255,176,32))
out=pathlib.Path(__file__).resolve().parents[1]/'MatheTricksTrainer'/'Assets.xcassets'/'AppIcon.appiconset'/'AppIcon.png'
img.resize((1024,1024),Image.LANCZOS).save(out)
print(out)
