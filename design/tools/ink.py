"""Turn the club's own car photos into navy ink-line drawings (transparent PNG).

Steps: upscale -> GrabCut car mask -> edge-only XDoG lines inside the mask ->
mask silhouette as a heavier outline -> plates blanked -> navy RGBA, cropped.
"""
import sys, json
import numpy as np
import cv2

NAVY = (0x14, 0x21, 0x3D)
HULLS = json.load(open('hulls.json'))
UP = 2  # work at 2x the 800px source

CARS = {
    # rect = GrabCut box at source scale (x, y, w, h); bg = definite-background boxes
    # plate = number-plate box to blank; out = output name
    'mustang': dict(src='assets/ku-mustang.jpg', rect=(48, 232, 676, 268),
                    bg=[(0, 300, 62, 170)], plate=(247, 380, 66, 20), out='ink-mustang.png', sky=270, canny=(30, 90, 40), sill=446),
    'supra': dict(src='assets/ku-supra-grey.jpg', rect=(26, 270, 760, 352),
                  bg=[], plate=(686, 497, 76, 27), out='ink-supra.png', canny=(45, 120, 70), sill=560),
}


def car_mask(src, hull, sky=0, fg=None, bg=None):
    """GrabCut seeded by a rough hull drawn round the car in the photo, run at
    source scale, then upscaled and smoothed so the silhouette reads as one clean line."""
    h, w = src.shape[:2]
    poly = np.zeros((h, w), np.uint8)
    cv2.fillPoly(poly, [np.array(hull, np.int32)], 255)
    k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))
    m = np.full((h, w), cv2.GC_BGD, np.uint8)
    m[cv2.dilate(poly, k(17)) > 0] = cv2.GC_PR_BGD
    m[poly > 0] = cv2.GC_PR_FGD
    m[cv2.erode(poly, k(31)) > 0] = cv2.GC_FGD
    if sky:  # bright, grey haze above the roofline is never car
        hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
        yy = np.arange(h)[:, None] < sky
        m[yy & (hsv[..., 2] > 200) & (hsv[..., 1] < 50)] = cv2.GC_BGD
    for P in (bg or []):
        t = np.zeros((h, w), np.uint8); cv2.fillPoly(t, [np.array(P, np.int32)], 255); m[t > 0] = cv2.GC_BGD
    for P in (fg or []):
        t = np.zeros((h, w), np.uint8); cv2.fillPoly(t, [np.array(P, np.int32)], 255); m[t > 0] = cv2.GC_FGD
    bgd = np.zeros((1, 65), np.float64); fgd = np.zeros((1, 65), np.float64)
    sm = cv2.bilateralFilter(src, 7, 30, 5)
    cv2.grabCut(sm, m, None, bgd, fgd, 8, cv2.GC_INIT_WITH_MASK)
    fg = np.where((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k(9))
    n, lab, st, _ = cv2.connectedComponentsWithStats(fg)
    if n > 1:
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        fg = np.where(lab == big, 255, 0).astype(np.uint8)
    cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    fill = np.zeros_like(fg); cv2.drawContours(fill, cnts, -1, 255, -1)
    fill = cv2.morphologyEx(fill, cv2.MORPH_OPEN, k(5))
    fill = cv2.bitwise_and(fill, cv2.dilate(poly, k(5)))  # the hull is a hard limit
    up = cv2.resize(fill, None, fx=UP, fy=UP, interpolation=cv2.INTER_LINEAR)
    up = cv2.GaussianBlur(up, (0, 0), 2.2)
    return np.where(up > 127, 255, 0).astype(np.uint8)


def xdog_lines(gray, sigma=1.1, k=1.6, tau=0.985, eps=-0.012, phi=60.0):
    g = gray.astype(np.float32) / 255.0
    g1 = cv2.GaussianBlur(g, (0, 0), sigma)
    g2 = cv2.GaussianBlur(g, (0, 0), sigma * k)
    d = g1 - tau * g2
    # edge-only: ink where the DoG dips below eps (an edge on the dark side), soft ramp
    ink = np.where(d < eps, np.clip(-np.tanh(phi * (d - eps)), 0, 1), 0.0)
    return ink.astype(np.float32)


def canny_lines(gray, lo, hi, minlen=40, width=3):
    e = cv2.Canny(gray, lo, hi, L2gradient=True)
    n, lab, st, _ = cv2.connectedComponentsWithStats(e, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= minlen
    e = (keep[lab] * 255).astype(np.uint8)
    e = cv2.dilate(e, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (width, width)))
    return cv2.GaussianBlur(e, (0, 0), 0.8).astype(np.float32) / 255


def run(name, cfg, debug=False):
    src = cv2.imread(cfg['src'])
    img = cv2.resize(src, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
    mask = car_mask(src, HULLS[name], cfg.get('sky', 0))
    s = img
    for _ in range(3):
        s = cv2.bilateralFilter(s, 9, 35, 7)
    gray = cv2.cvtColor(s, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8)).apply(gray)
    lo, hi, minlen = cfg['canny']
    thin = canny_lines(gray, lo, hi, minlen, width=3)
    bold = xdog_lines(gray, sigma=2.4, eps=cfg.get('bold_eps', -0.022))
    bold = np.where(bold > 0.5, bold, 0)
    ink = np.maximum(thin * 0.92, bold)
    inner = cv2.erode(mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    ink *= (inner > 0)
    b = (ink > 0.35).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(b, connectivity=8)
    keep = np.zeros(n, bool); keep[1:] = st[1:, cv2.CC_STAT_AREA] >= 60
    ink *= keep[lab]
    # silhouette: smoothed contour, drawn only above the sill so the underside stays open
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    c = max(cnts, key=cv2.contourArea)[:, 0, :].astype(np.float32)
    sig = 9.0
    r = int(sig * 3)
    kern = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); kern /= kern.sum()
    pad = np.vstack([c[-r:], c, c[:r]])
    sm = np.stack([np.convolve(pad[:, i], kern, mode='valid') for i in (0, 1)], 1)
    ycut = cfg['sill'] * UP
    sil = np.zeros(mask.shape, np.uint8)
    seg = []
    for p in list(sm) + [sm[0]]:
        if p[1] < ycut:
            seg.append(p)
        elif seg:
            if len(seg) > 4:
                cv2.polylines(sil, [np.round(np.array(seg) * 4).astype(np.int32)], False, 255, 4,
                              lineType=cv2.LINE_AA, shift=2)
            seg = []
    if len(seg) > 4:
        cv2.polylines(sil, [np.round(np.array(seg) * 4).astype(np.int32)], False, 255, 4,
                      lineType=cv2.LINE_AA, shift=2)
    ink = np.maximum(ink, sil.astype(np.float32) / 255.0)
    # blank the number plate: erase its lines, draw an empty plate outline
    x, y, w, h = (int(v * UP) for v in cfg['plate'])
    ink[y - 2:y + h + 2, x - 2:x + w + 2] = 0
    plate = np.zeros(mask.shape, np.uint8)
    cv2.rectangle(plate, (x, y), (x + w, y + h), 255, 3, lineType=cv2.LINE_AA)
    ink = np.maximum(ink, plate.astype(np.float32) / 255.0)
    # crop to the car with a margin
    ys, xs = np.where(mask > 0)
    pad = 24
    y0, y1 = max(0, ys.min() - pad), min(mask.shape[0], ys.max() + pad)
    x0, x1 = max(0, xs.min() - pad), min(mask.shape[1], xs.max() + pad)
    a = (np.clip(ink, 0, 1) * 255).astype(np.uint8)[y0:y1, x0:x1]
    rgba = np.zeros((a.shape[0], a.shape[1], 4), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = NAVY[2], NAVY[1], NAVY[0]  # BGR order for cv2
    rgba[..., 3] = a
    cv2.imwrite(cfg['out'], rgba)
    if debug:
        dbg = img.copy(); dbg[mask == 0] = (dbg[mask == 0] * 0.25).astype(np.uint8)
        cv2.imwrite(f'/tmp/dbg-mask-{name}.jpg', cv2.resize(dbg, None, fx=0.5, fy=0.5))
        prev = np.full((a.shape[0], a.shape[1], 3), (0xD8, 0xEB, 0xF3), np.uint8)  # cream (BGR)
        al = a.astype(np.float32)[..., None] / 255.0
        prev = (prev * (1 - al) + np.array([0x3D, 0x21, 0x14]) * al).astype(np.uint8)
        cv2.imwrite(f'/tmp/dbg-ink-{name}.png', prev)
    return dict(name=name, w=int(x1 - x0), h=int(y1 - y0), crop=[int(x0), int(y0), int(x1), int(y1)])


if __name__ == '__main__':
    names = sys.argv[1:] or list(CARS)
    print(json.dumps([run(n, CARS[n], debug=True) for n in names]))
