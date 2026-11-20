import math, json, random
SW, SH = 1360, 740
GAP = 14
P1=(697,0); P2=(697,196); P3=(566,367); P4=(676,440); P5=(1170,440); P6=(1212,494); P7=(1360,420); P8=(1075,590); P9=(1030,740)
REG = {
 'title': [(0,0),P1,P2,P3,(0,367)],
 'carA':  [P1,(SW,0),P7,P6,P5,P4,P3,P2],
 'carB':  [(0,367),P3,P4,P5,P6,P8,P9,(0,SH)],
 'meet':  [P6,P7,(SW,SH),P9,P8],
}
def area(p): return sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p)))/2
def inset(p, d):
    n=len(p); s=1 if area(p)>0 else -1   # y-down coords: area>0 means clockwise on screen
    lines=[]
    for i in range(n):
        a=p[i]; b=p[(i+1)%n]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
        nx,ny=(-dy/L, dx/L)  # left normal
        nx,ny = nx*s, ny*s
        lines.append(((a[0]+nx*d, a[1]+ny*d),(dx,dy)))
    out=[]
    for i in range(n):
        (p1,d1)=lines[i-1]; (p2,d2)=lines[i]
        den=d1[0]*d2[1]-d1[1]*d2[0]
        if abs(den)<1e-9: out.append(p2); continue
        t=((p2[0]-p1[0])*d2[1]-(p2[1]-p1[1])*d2[0])/den
        out.append((p1[0]+d1[0]*t, p1[1]+d1[1]*t))
    return out
def rounded(p, r):
    n=len(p); segs=[]
    for i in range(n):
        v=p[i]; a=p[i-1]; b=p[(i+1)%n]
        da=(a[0]-v[0],a[1]-v[1]); db=(b[0]-v[0],b[1]-v[1]); la=math.hypot(*da); lb=math.hypot(*db)
        ua=(da[0]/la,da[1]/la); ub=(db[0]/lb,db[1]/lb)
        cosang=max(-1,min(1,ua[0]*ub[0]+ua[1]*ub[1])); phi=math.acos(cosang)
        t=r/math.tan(phi/2) if phi>1e-3 else 0
        t=min(t,0.45*la,0.45*lb)
        s=(v[0]+ua[0]*t, v[1]+ua[1]*t); e=(v[0]+ub[0]*t, v[1]+ub[1]*t)
        segs.append((s,v,e))
    return segs
def bez(p0,c1,c2,p3,n=10):
    pts=[]
    for k in range(n+1):
        t=k/n; u=1-t
        pts.append((u**3*p0[0]+3*u*u*t*c1[0]+3*u*t*t*c2[0]+t**3*p3[0], u**3*p0[1]+3*u*u*t*c1[1]+3*u*t*t*c2[1]+t**3*p3[1]))
    return pts
def outline_pts(segs):
    pts=[]
    for (s,v,e) in segs:
        c1=(s[0]+(v[0]-s[0])*0.55, s[1]+(v[1]-s[1])*0.55); c2=(e[0]+(v[0]-e[0])*0.55, e[1]+(v[1]-e[1])*0.55)
        pts += bez(s,c1,c2,e)
    return pts
def path_d(segs, fx, fy, prec=4):
    f=lambda q: f"{round(fx(q[0]),prec)} {round(fy(q[1]),prec)}"
    d=f"M{f(segs[0][2])}"
    for i in range(1,len(segs)+1):
        s,v,e=segs[i%len(segs)]
        c1=(s[0]+(v[0]-s[0])*0.55, s[1]+(v[1]-s[1])*0.55); c2=(e[0]+(v[0]-e[0])*0.55, e[1]+(v[1]-e[1])*0.55)
        d+=f" L{f(s)} C{f(c1)} {f(c2)} {f(e)}"
    return d+" Z"
def resample(pts, step, closed=True):
    P=pts+[pts[0]] if closed else pts
    out=[P[0]]; acc=0
    for i in range(1,len(P)):
        a=P[i-1]; b=P[i]; L=math.hypot(b[0]-a[0],b[1]-a[1])
        if L==0: continue
        dist=step-acc
        while dist<=L:
            t=dist/L; out.append((a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)); dist+=step
        acc=L-(dist-step)
    return out
def rough(pts, seed, amp=1.6, passes=2, closed=True, step=7, overshoot=10, prec=1, off=1.2):
    rnd=random.Random(seed); ds=[]
    base=resample(pts, step, closed)
    n=len(base)
    for p in range(passes):
        ph=[rnd.uniform(0,6.28) for _ in range(3)]; fr=[rnd.uniform(0.6,1.4),rnd.uniform(1.8,3.2),rnd.uniform(5,8)]
        offx,offy=rnd.uniform(-off,off),rnd.uniform(-off,off)
        start=rnd.randint(0,n-1) if closed else 0
        seq=[base[(start+k)%n] for k in range(n)] if closed else base
        if closed: seq=seq+seq[:max(1,int(overshoot/step))]
        out=[]
        m=len(seq)
        for k,q in enumerate(seq):
            a=seq[max(0,k-1)]; b=seq[min(m-1,k+1)]
            tx,ty=b[0]-a[0],b[1]-a[1]; L=math.hypot(tx,ty) or 1
            nx,ny=-ty/L,tx/L; u=k/max(1,m-1)
            j=amp*(0.6*math.sin(fr[0]*u*6.28+ph[0])+0.3*math.sin(fr[1]*u*6.28+ph[1])+0.1*math.sin(fr[2]*u*6.28+ph[2]))
            out.append((q[0]+nx*j+offx, q[1]+ny*j+offy))
        ds.append("M"+" L".join(f"{round(x,prec)} {round(y,prec)}" for x,y in out))
    return " ".join(ds)

res={'stage':[SW,SH],'tiles':{}}
for k,p in REG.items():
    q=inset(p, GAP/2)
    segs=rounded(q, 26 if k!='meet' else 24)
    xs=[a[0] for a in q]; ys=[a[1] for a in q]
    bx,by,bw,bh=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
    clip=path_d(segs, lambda x:(x-bx)/bw, lambda y:(y-by)/bh)
    sk=rough(outline_pts(segs), seed=hash(k)%1000, amp=1.5, passes=2)
    res['tiles'][k]={'box':[round(bx,2),round(by,2),round(bw,2),round(bh,2)],
      'pct':[round(bx/SW*100,4),round(by/SH*100,4),round(bw/SW*100,4),round(bh/SH*100,4)],
      'clip':clip,'sketch':sk}
json.dump(res,open('geom.json','w'))
for k,v in res['tiles'].items(): print(k, v['box'], v['pct'], len(v['sketch']))
