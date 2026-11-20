"""Ink-line sketches of the five new club photos, same look as ink.py.

Each car: crop -> small copy (~800px) for the GrabCut cut-out seeded by a hull
guide -> line tracing on a 2x copy -> outline above the sill -> optional fade
where something in front hides the car -> navy RGBA, cropped to the car.
"""
import sys, json
import numpy as np
import cv2
sys.path.insert(0, '/home/claude/kupage')
from ink import car_mask, xdog_lines, canny_lines, UP, NAVY

C = json.load(open('/home/claude/kupage/crops5.json'))
CARS = {
    'p992': dict(hull=[(48,224),(46,150),(60,126),(104,102),(184,74),(264,52),(344,52),(418,74),(480,106),(552,118),(632,130),(706,146),(754,178),(768,206),(764,242),(724,266),(574,268),(568,276),(466,276),(462,244),(206,242),(204,250),(100,250),(98,226)],
                 plates=[(729,201,30,22)], sill=238, canny=(30, 90, 50)),
    'p930': dict(hull=[(50,184),(52,166),(68,128),(160,110),(240,100),(264,94),(320,58),(376,50),(450,52),(546,86),(578,116),(710,118),(712,134),(690,142),(684,156),(704,190),(722,204),(718,222),(690,236),(530,240),(528,274),(436,274),(432,232),(198,232),(196,246),(100,246),(98,226),(62,216)],
                 plates=[(682,194,24,32)], sill=226, canny=(16, 48, 130), clahe=5.0),
    'p918': dict(hull=[(38,226),(58,166),(92,146),(160,128),(202,106),(238,104),(250,124),(302,70),(360,54),(450,52),(560,66),(594,78),(664,98),(722,110),(750,138),(762,172),(762,240),(758,268),(696,268),(690,262),(482,266),(478,314),(392,314),(388,298),(50,292),(42,272)],
                 plates=[], sill=258, canny=(35, 100, 50)),
    'ferrari': dict(hull=[(30,134),(36,158),(40,180),(88,194),(118,196),(120,218),(250,218),(250,194),(610,194),(612,236),(746,236),(752,198),(790,172),(790,112),(774,70),(744,66),(600,54),(482,38),(416,22),(344,22),(304,34),(242,54),(160,66),(96,74),(60,100)],
                    plates=[], sill=190, destripe=True, sig=22.0, open=15, wheels=[(186,164,74),(676,170,74)]),
    'p964': dict(hull=[(20,212),(44,140),(72,126),(160,110),(296,82),(352,30),(400,18),(512,22),(578,34),(664,58),(790,66),(796,96),(762,104),(762,130),(798,156),(802,218),(632,234),(560,270),(352,330),(320,324),(172,302),(168,258),(62,250),(24,242)],
                 plates=[], sill=214, canny=(50, 130, 80), fade=True),
    'r33': dict(hull=[(34,226),(50,186),(86,158),(198,126),(262,106),(266,86),(292,86),(352,38),(416,28),(576,26),(634,38),(690,66),(734,74),(736,94),(758,120),(758,202),(746,266),(720,268),(714,246),(556,286),(552,366),(470,366),(462,350),(240,354),(72,334),(22,318)],
                plates=[(106,270,76,52)], sill=300, canny=(16, 48, 130), clahe=5.0),
    'p993': dict(hull=[(26,214),(36,186),(52,156),(88,138),(200,110),(276,102),(336,38),(384,26),(480,24),(578,42),(656,78),(696,86),(758,92),(760,110),(762,138),(774,156),(772,214),(742,250),(664,252),(660,232),(402,244),(400,302),(300,302),(296,290),(152,290),(32,266)],
                 plates=[(54,226,28,20)], sill=236, canny=(20, 60, 90), clahe=4.0),
    'r8': dict(hull=[(22,206),(42,172),(88,138),(192,118),(262,46),(336,26),(448,28),(552,50),(632,74),(688,78),(748,98),(756,126),(778,166),(782,266),(776,278),(720,278),(714,272),(556,306),(552,366),(458,366),(450,352),(240,354),(32,334),(20,314)],
               plates=[(98,258,76,32)], sill=300, canny=(30, 90, 50), wheels=[(504,290,78),(748,214,72)]),
    'senna': dict(hull=[(28,200),(26,112),(26,86),(14,80),(12,40),(30,30),(120,24),(232,24),(262,36),(320,26),(418,34),(562,102),(642,118),(722,150),(758,170),(762,228),(774,248),(720,278),(424,286),(420,290),(324,290),(320,250),(92,240),(36,240)],
                  plates=[], sill=230, canny=(30, 90, 50), wheels=[(372,222,62),(62,178,54)],
                  holes=[[(60,55),(88,55),(91,58),(91,76),(88,79),(60,79),(57,76),(57,58)], [(122,55),(195,55),(198,59),(198,62),(172,82),(122,80),(119,77),(119,58)]],
                  fg=[[(56,40),(234,35),(234,49),(56,53)], [(96,52),(114,52),(114,78),(96,78)], [(202,42),(220,42),(220,60),(202,64)], [(20,44),(52,44),(52,74),(20,74)]],
                  inpaint=dict(rects=[(350, 1180, 406, 1545), (1431, 1128, 1487, 1545)], rope=(1050, 1320))),
    'amggt': dict(hull=[(0,162),(80,146),(164,120),(206,118),(264,54),(400,26),(560,22),(626,26),(682,78),(692,72),(750,86),(752,116),(700,142),(758,152),(778,184),(782,210),(782,350),(770,356),(700,404),(698,598),(608,600),(560,618),(480,666),(240,670),(0,666)],
                  plates=[(0,548,84,96,'erase')], sill=590, canny=(30, 90, 60), fadeleft=110),
}


PAINTED = None


def inpaint_full(full, spec):
    """Paint out a rope barrier and its posts that cross in front of the car."""
    m = np.zeros(full.shape[:2], np.uint8)
    for (a, b, c, d) in spec.get('rects', []):
        m[b:d, a:c] = 255
    if spec.get('rope'):
        y0, y1 = spec['rope']
        hsv = cv2.cvtColor(full, cv2.COLOR_BGR2HSV)
        red = (((hsv[..., 0] < 6) | (hsv[..., 0] > 172)) & (hsv[..., 1] > 140) & (hsv[..., 2] > 50)).astype(np.uint8) * 255
        red[:y0] = 0; red[y1:] = 0
        n, lab, st, _ = cv2.connectedComponentsWithStats(red)
        big = np.zeros(n, bool); big[1:] = st[1:, cv2.CC_STAT_WIDTH] > 300   # only the long rope, not brake calipers
        m = np.maximum(m, (big[lab] * 255).astype(np.uint8))
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    global PAINTED
    PAINTED = m
    return cv2.inpaint(full, m, 9, cv2.INPAINT_TELEA)


def build(name, cfg, debug=True):
    c = C[name]
    full = cv2.imread(f'/home/claude/kupage/src5/{name}.jpg')
    if cfg.get('inpaint'):
        full = inpaint_full(full, cfg['inpaint'])
    x0, y0, x1, y1 = c['box']
    crop = full[y0:y1, x0:x1]
    s = c['s']
    small = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    H, W = small.shape[:2]
    hi = cv2.resize(crop, (W * UP, H * UP), interpolation=cv2.INTER_AREA if s * UP < 1 else cv2.INTER_CUBIC)
    mask = car_mask(small, cfg['hull'], fg=cfg.get('fg'), bg=cfg.get('holes'))
    for hole in cfg.get('holes', []):
        hm = np.zeros(mask.shape, np.uint8)
        cv2.fillPoly(hm, [np.array(hole, np.int32) * UP], 255)
        mask[hm > 0] = 0
    if cfg.get('open'):  # glass reflections nibble the cut-out: round it off
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cfg['open'] * 2 + 1,) * 2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (cfg['open'] * 2 + 1,) * 2))

    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))

    def traced(g, lo, hi_t, minlen, clip, bold=True):
        g = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8)).apply(g)
        L = canny_lines(g, lo, hi_t, minlen, width=3) * 0.92
        if bold:
            bb = xdog_lines(g, sigma=2.4, eps=-0.022)
            L = np.maximum(L, np.where(bb > 0.5, bb, 0))
        return L

    sm = hi
    for _ in range(3):
        sm = cv2.bilateralFilter(sm, 9, 35, 7)
    gray = cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY)
    if cfg.get('destripe'):
        # the wrap is thin dark stripes: close them up in saturation and brightness so
        # only the body's own edges remain; the wheels (no stripes) trace from the plain photo
        hsv = cv2.cvtColor(hi, cv2.COLOR_BGR2HSV)
        S_ = cv2.GaussianBlur(cv2.morphologyEx(hsv[..., 1], cv2.MORPH_CLOSE, k(13)), (0, 0), 3)
        V_ = cv2.GaussianBlur(cv2.morphologyEx(hsv[..., 2], cv2.MORPH_CLOSE, k(13)), (0, 0), 3)
        body = np.maximum(traced(S_, 25, 70, 80, 2.0, False), traced(V_, 30, 80, 80, 2.0, False))
        wm = np.zeros(gray.shape, np.uint8)
        for (cx, cy, r) in cfg['wheels']:
            cv2.circle(wm, (cx * UP, cy * UP), r * UP, 255, -1)
        wm = cv2.GaussianBlur(wm, (0, 0), 6) / 255.0
        ink = np.maximum(body * (1 - wm), traced(gray, 20, 60, 40, 3.0, False) * wm)
    else:
        lo, hi_t, minlen = cfg['canny']
        ink = traced(gray, lo, hi_t, minlen, cfg.get('clahe', 3.0))
        if cfg.get('wheels'):  # dark wheels in shade: trace them with more sensitive settings
            wm = np.zeros(gray.shape, np.uint8)
            for (cx, cy, r) in cfg['wheels']:
                cv2.circle(wm, (cx * UP, cy * UP), r * UP, 255, -1)
            wm = cv2.GaussianBlur(wm, (0, 0), 6) / 255.0
            ink = np.maximum(ink * (1 - wm), traced(gray, 14, 42, 70, 5.0, False) * wm)
    if cfg.get('inpaint'):  # no traced lines inside the painted-out rope and posts
        sup = cv2.resize(PAINTED, (full.shape[1], full.shape[0]))[y0:y1, x0:x1]
        sup = cv2.resize(sup, (W * UP, H * UP))
        sup = cv2.dilate(sup, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (17, 17)))
        sup = cv2.GaussianBlur(sup.astype(np.float32), (0, 0), 5) / 255.0
        ink *= 1 - np.clip(sup, 0, 1)
    inner = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    ink *= (inner > 0)
    b = (ink > 0.35).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 60
    ink *= keep[lab]

    # outline: smoothed contour, only above the sill
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cc = max(cnts, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    sig = cfg.get('sig', 9.0); r = int(sig * 3)
    kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); kern /= kern.sum()
    pad = np.vstack([cc[-r:], cc, cc[:r]])
    smc = np.stack([np.convolve(pad[:, i], kern, mode='valid') for i in (0, 1)], 1)
    ycut = cfg['sill'] * UP
    sil = np.zeros(mask.shape, np.uint8); seg = []

    def flush(seg):
        if len(seg) > 4:
            cv2.polylines(sil, [np.round(np.array(seg) * 4).astype(np.int32)], False, 255, 4,
                          lineType=cv2.LINE_AA, shift=2)
    edge = 6 * UP
    on_frame = lambda p: p[0] < edge or p[0] > mask.shape[1] - edge
    for p in list(smc) + [smc[0]]:
        if p[1] < ycut and not on_frame(p):
            seg.append(p)
        else:
            flush(seg); seg = []
    flush(seg)
    if cfg.get('holes'):  # outline the gaps under a wing too
        cn2, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
        for i, cn in enumerate(cn2):
            if hier[0][i][3] >= 0 and cv2.contourArea(cn) > 300 * UP * UP:
                cn = cv2.approxPolyDP(cn, 2.0, True)
                cv2.polylines(sil, [cn], True, 255, 3, lineType=cv2.LINE_AA)
    ink = np.maximum(ink, sil.astype(np.float32) / 255.0)

    for pl_ in cfg['plates']:
        px, py, pw, ph = pl_[:4]
        X, Y, Wp, Hp = (int(v * UP) for v in (px, py, pw, ph))
        ink[max(0, Y - 2):Y + Hp + 2, max(0, X - 2):X + Wp + 2] = 0
        if len(pl_) > 4:
            continue
        pl = np.zeros(mask.shape, np.uint8)
        cv2.rectangle(pl, (X, Y), (X + Wp, Y + Hp), 255, 3, lineType=cv2.LINE_AA)
        ink = np.maximum(ink, pl.astype(np.float32) / 255.0)

    if cfg.get('fade'):
        # where something in front hides the car, let the lines fade out instead of stopping dead
        dist = cv2.distanceTransform((mask > 0).astype(np.uint8), cv2.DIST_L2, 5)
        low = np.zeros_like(dist); low[int(cfg['sill'] * UP):, :] = 1
        low = cv2.GaussianBlur(low, (0, 0), 12)
        fade = np.clip(dist / 46.0, 0, 1)
        ink *= (1 - low) + low * fade

    if cfg.get('fadeleft'):  # the car runs off the photo's left edge: fade out towards it
        ramp = np.clip(np.arange(mask.shape[1]) / float(cfg['fadeleft'] * UP), 0, 1) ** 1.4
        ink *= ramp[None, :]
    ys, xs = np.where(mask > 0)
    padpx = 24
    Y0, Y1 = max(0, ys.min() - padpx), min(mask.shape[0], ys.max() + padpx)
    X0, X1 = max(0, xs.min() - padpx), min(mask.shape[1], xs.max() + padpx)
    a = (np.clip(ink, 0, 1) * 255).astype(np.uint8)[Y0:Y1, X0:X1]
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = NAVY[2], NAVY[1], NAVY[0]
    rgba[..., 3] = a
    cv2.imwrite(f'/home/claude/kupage/ink-{name}.png', rgba)
    if debug:
        dbg = small.copy(); m2 = cv2.resize(mask, (W, H)) > 0
        dbg[~m2] = (dbg[~m2] * 0.25).astype(np.uint8)
        cv2.imwrite(f'/tmp/dbg5-mask-{name}.jpg', dbg)
        prev = np.full(a.shape + (3,), (0xEC, 0xF6, 0xFA), np.float32)
        al = a.astype(np.float32)[..., None] / 255.0
        prev = prev * (1 - al) + np.array([0x3D, 0x21, 0x14], np.float32) * al
        cv2.imwrite(f'/tmp/dbg5-ink-{name}.png', cv2.resize(prev.astype(np.uint8), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    return dict(name=name, w=int(X1 - X0), h=int(Y1 - Y0))


if __name__ == '__main__':
    names = sys.argv[1:] or list(CARS)
    print(json.dumps([build(n, CARS[n]) for n in names]))
