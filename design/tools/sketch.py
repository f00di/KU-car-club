import math, json, random
exec(open('geom.py').read().split("res={'stage'")[0])
def circle(cx,cy,r,n=48): return [(cx+r*math.cos(2*math.pi*k/n), cy+r*math.sin(2*math.pi*k/n)) for k in range(n)]
def rrect(x,y,w,h,r): return outline_pts(rounded([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], r))
S={}
# icons, 48x48
S['wheel'] = rough(circle(24,24,18),11,0.7,2,True,2,6)+' '+rough(circle(24,24,5,24),12,0.4,1,True,1.5,3)+' '+rough([(19.5,24),(6.5,24)],13,0.4,1,False,1.5,0)+' '+rough([(28.5,24),(41.5,24)],14,0.4,1,False,1.5,0)+' '+rough([(24,29),(24,42)],15,0.4,1,False,1.5,0)
pin=[]
for k in range(0,41):
    a=math.pi*0.8+ (2*math.pi-1.6*math.pi*0.0)*0  # placeholder
cx,cy,r=24,19,12
arc=[(cx+r*math.cos(t), cy+r*math.sin(t)) for t in [math.pi*0.78+ (2*math.pi-2*0.78*math.pi+2*math.pi)*k/40 for k in range(41)]]
pinpts=[(24,43)]+[(cx+r*math.cos(t), cy+r*math.sin(t)) for t in [math.pi*(0.70)+ (math.pi*1.60)*k/40 for k in range(41)]]
S['pin']=rough(pinpts,21,0.6,2,True,2,4)+' '+rough(circle(24,19,4.5,20),22,0.3,1,True,1.5,2)
S['calendar']=rough(rrect(7,10,34,31,4),31,0.6,2,True,2,5)+' '+rough([(7,19),(41,19)],32,0.4,1,False,1.5,0)+' '+rough([(16,6),(16,13)],33,0.3,1,False,1,0)+' '+rough([(32,6),(32,13)],34,0.3,1,False,1,0)+' '+' '.join(rough(circle(x,y,1.2,8),40+i,0.1,1,True,0.8,0) for i,(x,y) in enumerate([(15,26),(24,26),(33,26),(15,34),(24,34)]))
S['people']=rough(circle(17,17,6,24),51,0.4,2,True,1.5,2)+' '+rough(circle(32,15,5,24),52,0.4,2,True,1.5,2)+' '+rough([(5,40)]+[(17+11*math.cos(t),36-10*math.sin(t)) for t in [math.pi-k*math.pi/20 for k in range(21)]]+[(29,40)],53,0.5,1,False,1.5,0)+' '+rough([(26,30)]+[(32+9*math.cos(t),34-9*math.sin(t)) for t in [math.pi*0.75-k*math.pi*0.75/16 for k in range(17)]]+[(43,37)],54,0.5,1,False,1.5,0)
S['flag']=rough([(12,43),(12,6)],61,0.4,1,False,1.5,0)+' '+rough([(12,8),(20,6),(28,10),(37,8),(37,24),(28,26),(20,22),(12,24)],62,0.5,2,True,1.5,3)
S['play']=rough([(18,13),(36,24),(18,35)],71,0.4,2,True,1.2,3)
S['arrowR']=rough([(10,24),(38,24)],81,0.5,2,False,1.5,0)+' '+rough([(28,14),(38,24),(28,34)],82,0.4,2,False,1.2,0)
S['arrowL']=rough([(38,24),(10,24)],83,0.5,2,False,1.5,0)+' '+rough([(20,14),(10,24),(20,34)],84,0.4,2,False,1.2,0)
S['spin']=rough([(24+15*math.cos(t),24+15*math.sin(t)) for t in [math.radians(-60+300*k/40) for k in range(41)]],91,0.5,1,False,1.5,0)+' '+rough([(31,6),(32.5,11),(27,13)],92,0.3,1,False,1,0)
# curly annotation arrow, 120x80, from top-left to bottom-right
def cat(pts,n=10):
    P=[pts[0]]+pts+[pts[-1]]; out=[]
    for i in range(1,len(P)-2):
        p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
        for k in range(n):
            u=k/n; u2=u*u; u3=u2*u
            out.append(tuple(0.5*((2*p1[j])+(-p0[j]+p2[j])*u+(2*p0[j]-5*p1[j]+4*p2[j]-p3[j])*u2+(-p0[j]+3*p1[j]-3*p2[j]+p3[j])*u3) for j in (0,1)))
    return out+[pts[-1]]
cur=cat([(6,16),(34,6),(64,14),(70,34),(56,42),(50,30),(64,24),(84,34),(100,52),(108,70)])
S['curl']=rough(cur,101,0.7,1,False,2,0)+' '+rough([(96,70),(108,71),(110,59)],102,0.4,1,False,1.2,0)
# hand underline, 300x24
S['underline']=rough(cat([(4,15),(70,9),(150,12),(230,7),(296,9),(250,15),(150,18),(60,19),(24,17)],8),111,1.0,1,False,2.5,0)
# scribble circle (around a word), 200x80
oval=[(100+92*math.cos(t),40+30*math.sin(t)) for t in [math.radians(200+380*k/60) for k in range(61)]]
S['oval']=rough(oval,121,1.8,1,False,3,0,1,0)
# pill (nav) 300x56, button 200x56, circle button 56x56, card frame 200x340
S['pill']=rough(rrect(3,3,294,50,25),131,2.0,2,True,4,18,1,2.2)
S['btn']=rough(rrect(3,3,194,50,14),141,1.8,2,True,4,16,1,2.0)
S['btnPill']=rough(rrect(3,3,194,50,25),151,1.8,2,True,4,16,1,2.0)
S['ring']=rough(circle(28,28,24,40),161,1.4,2,True,2,10,1,1.6)
S['frame']=rough(rrect(4,4,192,332,12),171,2.4,2,True,5,22,1,2.6)
S['dash']=rough([(2,6),(60,5),(118,7)],181,0.6,1,False,3,0)
json.dump(S,open('sketch.json','w'))
print({k:len(v) for k,v in S.items()})
