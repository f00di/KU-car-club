"""Refined ink sketches: clean, continuous, uniform lines traced from the club's own photos.

Per car: crop -> cut-out mask (same hull guides as before) -> lift the shadows ->
structured edge detection (OpenCV ximgproc, two scales) -> thin -> trace into
strokes -> bridge small gaps between strokes that line up -> drop scraps ->
smooth -> closed outline from the mask -> render navy on transparent + SVG.
Every line comes from the photo's own pixels.
"""
import sys, json, math
import numpy as np
import cv2
from scipy.spatial import cKDTree
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '/home/claude/kupage')
import ink, ink5

UP = 2
MODE = 'canny'
NAVY = (0x14, 0x21, 0x3D)
SED = cv2.ximgproc.createStructuredEdgeDetection('/home/claude/models/sed/testdata/cv/ximgproc/model.yml.gz')
ALL = ['supra', 'mustang', 'p992', 'p930', 'p918', 'ferrari', 'p964', 'r33', 'p993', 'r8', 'senna', 'amggt']

# per-car tuning on top of the earlier configs
TUNE = {
    'p930': dict(quiet=[[(345, 68), (432, 68), (432, 118), (345, 118)]]),   # driver behind the glass stays out
    'ferrari': dict(sig=16.0, destripe=True),
    'p964': dict(open_bottom=True),
    'amggt': dict(open_bottom=True),
}
K = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (r, r))

# rim guesses by eye in small-scale coords (cx, cy, rx, ry); the fit below snaps them to the photo's edges
WHEELS = {
    'mustang': [(388, 425, 34, 46), (660, 418, 28, 44)],
    'supra': [(285, 525, 38, 68), (58, 512, 24, 62)],
    'p992': [(152, 214, 45, 45), (516, 220, 45, 45)],
    'p930': [(142, 198, 30, 30), (480, 222, 32, 32)],
    'p918': [(432, 240, 36, 60), (726, 200, 26, 52)],
    'ferrari': [(186, 162, 44, 44), (678, 168, 46, 46)],
    'p964': [(390, 262, 46, 54), (730, 210, 28, 50)],
    'r33': [(512, 304, 32, 52), (740, 216, 14, 42)],
    'p993': [(350, 240, 44, 48), (706, 198, 32, 40)],
    'r8': [(508, 272, 36, 64), (752, 210, 22, 54)],
    'senna': [(370, 224, 40, 50), (66, 178, 22, 44)],
}
WHEEL_FIX = {
    'ferrari': {0: dict(rim=(362, 327, 85, 85), force=True), 1: dict(rim=(1344, 338, 86, 86), force=True)},
    'p964': {0: dict(rim=(779, 533, 95, 112), ky=1.2), 1: dict(rim=(1454, 436, 62, 112), ky=1.18)},
    'r33': {0: dict(rim=(1010, 592, 62, 142))},
    'p993': {0: dict(rim=(692, 487, 93, 114)), 1: dict(rim=(1408, 406, 60, 98))},
    'r8': {0: dict(rim=(1024, 538, 66, 136))},
    'senna': {0: dict(rim=(738, 454, 76, 98)), 1: dict(rim=(124, 360, 44, 92))},
}
NS = 96
_T = np.linspace(0, 2 * np.pi, NS, endpoint=False)
_CT, _ST = np.cos(_T), np.sin(_T)


def ell_pts(P):
    """P: (...,5) cx,cy,rx,ry,ang(rad) -> (...,NS,2)"""
    cx, cy, rx, ry, a = [P[..., i, None] for i in range(5)]
    x = rx * _CT; y = ry * _ST
    ca, sa = np.cos(a), np.sin(a)
    return np.stack([cx + x * ca - y * sa, cy + x * sa + y * ca], -1)


def sample(img, pts):
    h, w = img.shape
    xi = np.round(pts[..., 0]).astype(np.int64); yi = np.round(pts[..., 1]).astype(np.int64)
    ok = (xi >= 0) & (xi < w) & (yi >= 0) & (yi < h)
    out = np.zeros(xi.shape, np.float32)
    out[ok] = img[yi[ok], xi[ok]]
    return out


def best_ellipse(score_img, cands, weight_img=None):
    best = None
    for i in range(0, len(cands), 20000):
        P = cands[i:i + 20000]
        v = sample(score_img, ell_pts(P))
        sc = v.mean(-1)
        j = int(np.argmax(sc))
        if best is None or sc[j] > best[0]:
            best = (float(sc[j]), P[j].copy())
    return best


def grid(center, dc, n_c, rx_rng, ry_rng, n_r, angs, tall=True):
    cx0, cy0 = center
    g = np.meshgrid(np.linspace(cx0 - dc, cx0 + dc, n_c), np.linspace(cy0 - dc, cy0 + dc, n_c),
                    np.linspace(*rx_rng, n_r), np.linspace(*ry_rng, n_r), np.deg2rad(angs), indexing='ij')
    P = np.stack([a.ravel() for a in g], -1).astype(np.float32)
    if tall:
        P = P[P[:, 2] <= P[:, 3] * 1.06]
    return P


def fit_wheel(nms, mask, init):
    """-> dict(rim=(cx,cy,rx,ry,a), rim_cov, tyre=..., tyre_cov) in hi-res px"""
    cx, cy, rx, ry = [v * UP for v in init]
    eb = cv2.dilate((nms > 0.06).astype(np.uint8), K(7)).astype(np.float32)
    P = grid((cx, cy), 28, 9, (rx * 0.72, rx * 1.25), (ry * 0.78, ry * 1.22), 8, [-14, -7, 0, 7, 14])
    sc, b = best_ellipse(eb, P)
    eb2 = cv2.dilate((nms > 0.06).astype(np.uint8), K(3)).astype(np.float32)
    P = grid((b[0], b[1]), 6, 7, (b[2] * 0.93, b[2] * 1.07), (b[3] * 0.93, b[3] * 1.07), 7,
             np.rad2deg(b[4]) + np.array([-5, -2.5, 0, 2.5, 5]))
    sc2, rim = best_ellipse(eb2, P)
    # tyre: the rim scaled out, a touch wider for the tread; edges or the cut-out's own border count as support
    border = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, K(9)) > 0
    et = np.maximum(eb, border.astype(np.float32))
    ky = np.linspace(1.14, 1.62, 13); kx = np.linspace(1.0, 1.28, 6)
    dx = np.linspace(-10, 10, 5); dy = np.linspace(-6, 6, 4)
    g = np.meshgrid(ky, kx, dx, dy, indexing='ij')
    KY, KX, DX, DY = [a.ravel() for a in g]
    P = np.stack([rim[0] + DX, rim[1] + DY, rim[2] * KY * KX, rim[3] * KY, np.full_like(KY, rim[4])], -1).astype(np.float32)
    sc3, tyre = best_ellipse(et, P)
    return dict(rim=rim, rim_cov=sc2, tyre=tyre, tyre_cov=sc3)


def wheel_geometry(name, nms, mask):
    """-> list of dict(rim=P, tyre=P, force) for each wheel of this car (hi-res px)"""
    out = []
    h, w = mask.shape
    eb2 = cv2.dilate((nms > 0.06).astype(np.uint8), K(3)).astype(np.float32)
    for i, init in enumerate(WHEELS.get(name, [])):
        fix = WHEEL_FIX.get(name, {}).get(i, {})
        if 'rim' in fix:
            cx, cy, rx, ry = fix['rim']
            P = grid((cx, cy), 5, 5, (rx * 0.95, rx * 1.05), (ry * 0.95, ry * 1.05), 5, [-4, -2, 0, 2, 4])
            _, rim = best_ellipse(eb2, P)
        else:
            rim = fit_wheel(nms, mask, init)['rim']
        cx, cy, rx, ry, a = [float(v) for v in rim]
        ky = fix.get('ky')
        if ky is None:
            x0, x1 = int(max(0, cx - 0.6 * rx)), int(min(w, cx + 0.6 * rx))
            cols = np.flatnonzero(mask[:, x0:x1].any(axis=1))
            ky = (cols.max() - cy) / ry if len(cols) else 1.33
            if not (1.10 <= ky <= 1.75):
                ky = 1.33
        tyre = np.array([cx, cy, rx * ky, ry * ky, a], np.float32)
        out.append(dict(rim=np.array(rim, np.float32), tyre=tyre, force=fix.get('force', False)))
    return out


def arcs(P, support, close_deg=44, min_deg=30, full_if=0.70):
    """ellipse P with per-sample support -> list of polylines (only where the photo backs the curve)"""
    pts = ell_pts(P)
    n = len(support)
    if support.mean() >= full_if:
        return [np.vstack([pts, pts[:1]]).astype(np.float32)]
    sup = support.copy()
    gap = int(round(close_deg / 360 * n)); mn = int(round(min_deg / 360 * n))
    # close short gaps (circular)
    ext = np.concatenate([sup, sup, sup])
    idx = np.flatnonzero(ext)
    for a, b in zip(idx[:-1], idx[1:]):
        if 1 < b - a <= gap:
            ext[a:b] = True
    sup = ext[n:2 * n]
    if sup.all():
        return [np.vstack([pts, pts[:1]]).astype(np.float32)]
    out = []
    start = int(np.flatnonzero(~sup)[0])
    rolled = np.roll(sup, -start); rp = np.roll(pts, -start, axis=0)
    i = 0
    while i < n:
        if rolled[i]:
            j = i
            while j < n and rolled[j]:
                j += 1
            if j - i >= mn:
                out.append(rp[i:j].astype(np.float32))
            i = j
        else:
            i += 1
    return out


def inside_ellipse(P, pts, k=1.0):
    cx, cy, rx, ry, a = P
    d = pts - np.array([cx, cy], np.float32)
    ca, sa = math.cos(-a), math.sin(-a)
    x = d[:, 0] * ca - d[:, 1] * sa; y = d[:, 0] * sa + d[:, 1] * ca
    return (x / (rx * k)) ** 2 + (y / (ry * k)) ** 2 <= 1.0


def cut_keep(paths, keep_fn, minlen=2):
    out = []
    for p in paths:
        ok = keep_fn(p)
        if ok.all():
            out.append(p); continue
        idx = np.flatnonzero(ok)
        if len(idx) == 0:
            continue
        for run in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
            if len(run) >= minlen:
                out.append(p[run])
    return out


def prep(name):
    """-> hi (BGR, ~1600 wide), mask (uint8 at hi res), cfg, sup (painted-out strip mask or None)"""
    if name in ('mustang', 'supra'):
        cfg = dict(ink.CARS[name])
        src = cv2.imread('/home/claude/kupage/' + cfg['src'])
        hi = cv2.resize(src, None, fx=UP, fy=UP, interpolation=cv2.INTER_CUBIC)
        mask = ink.car_mask(src, ink.HULLS[name], cfg.get('sky', 0))
        cfg['plates'] = [cfg['plate']]
        cfg.update(TUNE.get(name, {}))
        return hi, mask, cfg, None
    cfg = dict(ink5.CARS[name]); cfg.update(TUNE.get(name, {}))
    c = ink5.C[name]
    full = cv2.imread(f'/home/claude/kupage/src5/{name}.jpg')
    sup = None
    if cfg.get('inpaint'):
        full = ink5.inpaint_full(full, cfg['inpaint'])
    x0, y0, x1, y1 = c['box']; s = c['s']
    crop = full[y0:y1, x0:x1]
    small = cv2.resize(crop, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    H, W = small.shape[:2]
    hi = cv2.resize(crop, (W * UP, H * UP), interpolation=cv2.INTER_AREA if s * UP < 1 else cv2.INTER_CUBIC)
    mask = ink.car_mask(small, cfg['hull'], fg=cfg.get('fg'), bg=cfg.get('holes'))
    for hole in cfg.get('holes', []):
        hm = np.zeros(mask.shape, np.uint8)
        cv2.fillPoly(hm, [np.array(hole, np.int32) * UP], 255)
        mask[hm > 0] = 0
    if cfg.get('open'):
        kk = K(cfg['open'] * 2 + 1)
        mask = cv2.morphologyEx(cv2.morphologyEx(mask, cv2.MORPH_OPEN, kk), cv2.MORPH_CLOSE, kk)
    if cfg.get('inpaint'):
        sup = ink5.PAINTED[y0:y1, x0:x1]
        sup = cv2.resize(sup, (W * UP, H * UP))
    return hi, mask, cfg, sup


def lift(hi, mask):
    """Denoise, then brighten so the car's median tone sits mid-grey: shadows give up their edges."""
    den = cv2.fastNlMeansDenoisingColored(hi, None, 4, 4, 5, 15)
    f = den.astype(np.float32) / 255.0
    lum = f.max(axis=2)
    med = float(np.median(lum[mask > 0]))
    gamma = float(np.clip(math.log(0.5) / math.log(max(med, 1e-3)), 0.38, 1.0))
    g = np.power(np.maximum(lum, 1e-4), gamma) / np.maximum(lum, 1e-4)
    return np.clip(f * g[..., None], 0, 1), gamma


def sed_edges(img01):
    return SED.detectEdges(np.ascontiguousarray(cv2.cvtColor(img01.astype(np.float32), cv2.COLOR_BGR2RGB)))


def edge_map(lifted, cfg):
    h, w = lifted.shape[:2]
    src = lifted
    if cfg.get('destripe'):
        # the wrap's thin stripes: close them up so the body's own lines remain
        u8 = (lifted * 255).astype(np.uint8)
        u8 = cv2.morphologyEx(u8, cv2.MORPH_CLOSE, K(13))
        u8 = cv2.GaussianBlur(u8, (0, 0), 2.5)
        src = u8.astype(np.float32) / 255.0
    e1 = sed_edges(src)
    half = cv2.resize(src, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
    e2 = cv2.resize(sed_edges(half), (w, h), interpolation=cv2.INTER_LINEAR)
    E = np.sqrt(np.clip(e1, 0, 1) * np.clip(e2, 0, 1)).astype(np.float32)
    o = SED.computeOrientation(E)
    nms = SED.edgesNms(E, o, r=2, s=0, m=1.0, isParallel=True)
    return E, nms


def canny_gated(lifted, E, cfg):
    u8 = (lifted * 255).astype(np.uint8)
    if cfg.get('destripe'):
        u8 = cv2.GaussianBlur(cv2.morphologyEx(u8, cv2.MORPH_CLOSE, K(13)), (0, 0), 2.5)
    sm = u8
    for _ in range(2):
        sm = cv2.bilateralFilter(sm, 9, 30, 7)
    g = cv2.createCLAHE(clipLimit=cfg.get('clip', 2.0), tileGridSize=(8, 8)).apply(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY))
    lo, hi = cfg.get('canny2', (26, 78))
    c = (cv2.Canny(g, lo, hi, L2gradient=True) > 0).astype(np.uint8)
    Ed = cv2.dilate(E, K(5))
    n, lab = cv2.connectedComponents(c, connectivity=8)
    sums = np.bincount(lab.ravel(), weights=Ed.ravel(), minlength=n); cnt = np.bincount(lab.ravel(), minlength=n)
    mean = sums / np.maximum(cnt, 1)
    keep = (mean > cfg.get('gate', 0.10)) & (cnt >= cfg.get('minpx', 14)); keep[0] = False
    return keep[lab]


def hysteresis(nms, lo, hi):
    weak = (nms > lo).astype(np.uint8)
    n, lab = cv2.connectedComponents(weak, connectivity=8)
    keep = np.zeros(n, bool)
    keep[np.unique(lab[nms > hi])] = True
    keep[0] = False
    return keep[lab]


def trace(skel):
    """1px skeleton -> list of ordered polylines (N,2 float, x,y). Junction pixels split strokes."""
    sk = (skel > 0).astype(np.uint8)
    # crossing number (0->1 transitions round the 8 neighbours): 1 = end, 2 = along a line, 3+ = a real junction.
    # Counting neighbours instead would call every diagonal stair-step a junction and chop curves to bits.
    p = np.pad(sk, 1)
    H, W = sk.shape
    sh = lambda dy, dx: p[1 + dy:1 + dy + H, 1 + dx:1 + dx + W]
    ring = [sh(-1, 0), sh(-1, 1), sh(0, 1), sh(1, 1), sh(1, 0), sh(1, -1), sh(0, -1), sh(-1, -1)]
    cn = np.zeros(sk.shape, np.int32)
    for i in range(8):
        cn += ((ring[i] == 0) & (ring[(i + 1) % 8] == 1)).astype(np.int32)
    simple = (sk > 0) & (cn < 3)
    ys, xs = np.nonzero(simple)
    pix = set(zip(ys.tolist(), xs.tolist()))
    OFF = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def nbrs(p):
        return [(p[0] + dy, p[1] + dx) for dy, dx in OFF if (p[0] + dy, p[1] + dx) in pix]
    deg = {p: len(nbrs(p)) for p in pix}
    seen = set(); paths = []

    def walk(start):
        path = [start]; seen.add(start); cur = start
        while True:
            nx = [q for q in nbrs(cur) if q not in seen]
            if not nx:
                break
            cur = nx[0]; seen.add(cur); path.append(cur)
        return path
    for p in sorted(pix, key=lambda q: deg[q]):      # endpoints first, loops last
        if p in seen:
            continue
        path = walk(p)
        if len(path) >= 2:
            paths.append(np.array([(x, y) for y, x in path], np.float32))
    return paths


def plen(p):
    return float(np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1)).sum()) if len(p) > 1 else 0.0


def end_dir(p, end, k=7):
    """unit vector pointing outward from the stroke at one end"""
    if end == 0:
        a, b = p[min(k, len(p) - 1)], p[0]
    else:
        a, b = p[max(len(p) - 1 - k, 0)], p[-1]
    d = b - a; n = float(np.hypot(*d))
    return d / n if n > 1e-6 else np.zeros(2, np.float32)


def link(paths, R=26.0, tight=5.0):
    """Bridge gaps between stroke ends that face each other and line up."""
    if not paths:
        return paths
    ends = []
    for i, p in enumerate(paths):
        for e in (0, 1):
            ends.append((i, e, p[0] if e == 0 else p[-1], end_dir(p, e)))
    pts = np.array([e[2] for e in ends])
    tree = cKDTree(pts)
    cands = []
    for a, b in tree.query_pairs(R):
        ia, ea, pa, da = ends[a]; ib, eb, pb, db = ends[b]
        if ia == ib:
            continue
        v = pb - pa; d = float(np.hypot(*v))
        if d < 1e-6:
            cands.append((0.0, a, b)); continue
        v = v / d
        ca = float(da @ v); cb = float(db @ -v); cc = float(da @ db)
        if d <= tight:
            if cc < 0.0:                                  # facing each other
                cands.append((d + 14 * (1 + cc), a, b))
        else:
            lim = 0.88 if d < 14 else (0.94 if d < 26 else 0.975)   # further apart -> must line up better
            if ca > lim and cb > lim and cc < -0.7:
                cands.append((d + 30 * (2 - ca - cb), a, b))
    cands.sort()
    partner = {}
    for _, a, b in cands:
        if a in partner or b in partner:
            continue
        partner[a] = b; partner[b] = a
    used = [False] * len(paths); out = []
    for i in range(len(paths)):
        if used[i]:
            continue
        # walk back to a chain start
        start, send = i, 0
        guard = 0
        while (2 * start + send) in partner and guard < len(paths):
            j = partner[2 * start + send]; nxt, ne = j // 2, j % 2
            if nxt == i:
                break
            start, send = nxt, 1 - ne; guard += 1
        chain = []; cur, cend = start, send                # cend = the end we enter from
        while True:
            used[cur] = True
            p = paths[cur]
            chain.append(p if cend == 0 else p[::-1])
            out_end = 1 - cend
            key = 2 * cur + out_end
            if key not in partner:
                break
            j = partner[key]; nxt, ne = j // 2, j % 2
            if used[nxt]:
                break
            cur, cend = nxt, ne
        out.append(np.vstack(chain))
    return out


def smooth(p, sigma=3.0, step=2.0, closed=False):
    if len(p) < 3:
        return p
    seg = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1)); t = np.concatenate([[0], np.cumsum(seg)])
    L = t[-1]
    if L < step * 2:
        return p
    n = max(int(L / step), 3)
    tt = np.linspace(0, L, n)
    q = np.stack([np.interp(tt, t, p[:, 0]), np.interp(tt, t, p[:, 1])], 1)
    s = sigma / step
    if closed:
        return np.stack([gaussian_filter1d(q[:, i], s, mode='wrap') for i in (0, 1)], 1).astype(np.float32)
    r = int(s * 3) + 1
    head = 2 * q[0] - q[1:r + 1][::-1]; tail = 2 * q[-1] - q[-r - 1:-1][::-1]   # point-reflect: ends stay put
    pad = np.vstack([head, q, tail])
    sm = np.stack([gaussian_filter1d(pad[:, i], s, mode='nearest') for i in (0, 1)], 1)
    return sm[len(head):len(head) + len(q)].astype(np.float32)


def wiggle(p):
    """mean absolute turning per pixel of length (after smoothing): scribbles score high"""
    if len(p) < 5:
        return 9.0
    d = p[1:] - p[:-1]; a = np.arctan2(d[:, 1], d[:, 0])
    da = np.angle(np.exp(1j * (a[1:] - a[:-1])))
    return float((np.abs(da).sum() - abs(da.sum())) / max(plen(p), 1e-6))


def cut_inside(paths, bad):
    """split strokes where they pass through bad (bool mask)"""
    out = []
    h, w = bad.shape
    for p in paths:
        xi = np.clip(np.round(p[:, 0]).astype(int), 0, w - 1); yi = np.clip(np.round(p[:, 1]).astype(int), 0, h - 1)
        ok = ~bad[yi, xi]
        if ok.all():
            out.append(p); continue
        idx = np.flatnonzero(ok)
        if len(idx) == 0:
            continue
        for run in np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1):
            if len(run) >= 2:
                out.append(p[run])
    return out


def outline(mask, cfg):
    """closed, smoothed silhouette (list of strokes; open where the car is hidden or leaves the frame)"""
    cnts, hier = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    outer = max([c for i, c in enumerate(cnts) if hier[0][i][3] < 0], key=cv2.contourArea)[:, 0, :].astype(np.float32)
    sig = cfg.get('sig', 7.0)
    sm = smooth(outer, sigma=sig, step=2.0, closed=True)
    if 'sill' in cfg:                                   # calmer line along the underside, where the cut-out follows shadow
        low = smooth(outer, sigma=cfg.get('sig_low', 20.0), step=2.0, closed=True)
        n = min(len(sm), len(low)); sm, low = sm[:n], low[:n]
        t = np.clip((sm[:, 1] - (cfg['sill'] * UP - 24)) / 48.0, 0, 1)[:, None]
        sm = (sm * (1 - t) + low * t).astype(np.float32)
    strokes = []
    h, w = mask.shape
    if cfg.get('open_bottom'):
        ycut = cfg['sill'] * UP; edge = 6 * UP
        ok = (sm[:, 1] < ycut) & (sm[:, 0] > edge) & (sm[:, 0] < w - edge)
        idx = np.flatnonzero(ok)
        runs = np.split(idx, np.flatnonzero(np.diff(idx) > 1) + 1) if len(idx) else []
        if len(runs) > 1 and ok[0] and ok[-1]:
            runs = [np.concatenate([runs[-1], runs[0]])] + runs[1:-1]
        strokes += [sm[r] for r in runs if len(r) > 4]
    else:
        strokes.append(np.vstack([sm, sm[:1]]))
    for i, c in enumerate(cnts):                       # gaps inside the cut-out (under a wing)
        if hier[0][i][3] >= 0 and cv2.contourArea(c) > 300 * UP * UP:
            q = smooth(c[:, 0, :].astype(np.float32), sigma=3.0, step=2.0, closed=True)
            strokes.append(np.vstack([q, q[:1]]))
    return strokes


def render(shape, strokes_w, ss=2):
    """strokes_w: list of (polyline, width px). -> float alpha (h,w)"""
    h, w = shape
    canvas = np.zeros((h * ss, w * ss), np.uint8)
    for p, wd in strokes_w:
        if len(p) < 2:
            continue
        pts = np.round(p * ss * 8).astype(np.int32)
        th = max(int(round(wd * ss)), 1)
        cv2.polylines(canvas, [pts], False, 255, th, lineType=cv2.LINE_AA, shift=3)
        for e in (pts[0], pts[-1]):                          # round caps
            cv2.circle(canvas, (int(e[0]), int(e[1])), int(th * 4), 255, -1, lineType=cv2.LINE_AA, shift=3)
    return cv2.resize(canvas, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0


def svg_path(p, ox, oy, prec=1):
    q = cv2.approxPolyDP(p.reshape(-1, 1, 2).astype(np.float32), 0.6, False)[:, 0, :]
    return 'M' + ' L'.join(f'{round(float(x - ox), prec)} {round(float(y - oy), prec)}' for x, y in q)


def build(name, debug=True, lo=None, hi_t=None):
    hi, mask, cfg, sup = prep(name)
    h, w = mask.shape
    lifted, gamma = lift(hi, mask)
    E, nms = edge_map(lifted, cfg)
    lo = lo if lo is not None else cfg.get('lo', 0.06)
    hi_t = hi_t if hi_t is not None else cfg.get('hi', 0.14)
    edges = canny_gated(lifted, E, cfg) if MODE == 'canny' else hysteresis(nms, lo, hi_t)
    dist = cv2.distanceTransform((mask > 0).astype(np.uint8), cv2.DIST_L2, 5)
    edges &= dist > 9                                         # the outline itself comes from the cut-out
    if sup is not None:
        edges &= cv2.dilate(sup, K(9)) == 0                   # nothing traced inside the painted-out strips
    skel = cv2.ximgproc.thinning(edges.astype(np.uint8) * 255) > 0
    paths = trace(skel)
    paths = [p for p in paths if len(p) >= 4]
    paths = link(paths, R=cfg.get('R', 34.0))

    # wheels: clean ellipses fitted to the photo, drawn where the photo backs them
    wheels = wheel_geometry(name, nms, mask)
    near_edge = cv2.dilate((nms > 0.05).astype(np.uint8), K(9)) > 0
    border = cv2.morphologyEx(mask, cv2.MORPH_GRADIENT, K(13)) > 0
    inmask = cv2.dilate(mask, K(13)) > 0
    wheel_strokes = []
    for wh in wheels:
        rim, tyre = wh['rim'], wh['tyre']
        pr = ell_pts(rim); pt = ell_pts(tyre)
        ok_r = sample(inmask.astype(np.float32), pr) > 0
        sup_r = (sample(near_edge.astype(np.float32), pr) > 0) & ok_r
        if wh['force'] or sup_r.mean() >= 0.45:
            sup_r = ok_r.copy()
        wh['rim_arcs'] = arcs(rim, sup_r, full_if=0.92)
        ok_t = sample(inmask.astype(np.float32), pt) > 0
        sup_t = ((sample(near_edge.astype(np.float32), pt) > 0) | (sample(border.astype(np.float32), pt) > 0)) & ok_t
        lower = _ST > 0.15                                     # the ground half is always drawn
        sup_t |= lower & ok_t
        if wh['force']:
            sup_t = ok_t.copy()
        wh['tyre_arcs'] = arcs(tyre, sup_t, full_if=0.92)
        wheel_strokes += wh['rim_arcs'] + wh['tyre_arcs']

    scored = []
    for p in paths:
        L = plen(p)
        xi = np.clip(np.round(p[:, 0]).astype(int), 0, w - 1); yi = np.clip(np.round(p[:, 1]).astype(int), 0, h - 1)
        sc_ = float(E[yi, xi].mean())
        scored.append((smooth(p, sigma=cfg.get('ssig', 3.2)), L, sc_))
    Lmin = cfg.get('Lmin', 26.0 if MODE == 'canny' else 40.0)
    keep = []
    for q, L, sc_ in scored:
        mid = q[len(q) // 2][None, :]
        in_rim = any(inside_ellipse(wh['rim'], mid, 0.97)[0] for wh in wheels)
        if in_rim:
            if L >= 30 and wiggle(q) < 0.16:
                keep.append(q)
            continue
        if L < Lmin:
            continue
        if L < 70 and wiggle(q) > (0.14 if MODE == 'canny' else 0.05):   # short and scribbly
            continue
        if L < 60 and sc_ < (0.12 if MODE == 'canny' else 0.18):          # short and faint
            continue
        keep.append(q)
    # strokes: nothing on the tyre sidewall or doubling the fitted ellipses
    for wh in wheels:
        rim, tyre = wh['rim'], wh['tyre']
        keep = cut_keep(keep, lambda p: ~(inside_ellipse(tyre, p, 1.04) & ~inside_ellipse(rim, p, 0.93)))
    keep = [p for p in keep if plen(p) >= 12]
    # plates, people behind glass
    bad = np.zeros((h, w), bool)
    plate_strokes = []
    for pl in cfg.get('plates', []):
        px, py, pw, ph = (int(v * UP) for v in pl[:4])
        bad[max(0, py - 4):py + ph + 4, max(0, px - 4):px + pw + 4] = True
        if len(pl) == 4:
            r = 5
            box = np.array([(px + r, py), (px + pw - r, py), (px + pw, py + r), (px + pw, py + ph - r), (px + pw - r, py + ph),
                            (px + r, py + ph), (px, py + ph - r), (px, py + r), (px + r, py)], np.float32)
            plate_strokes.append(box)
    for poly in cfg.get('quiet', []):
        t = np.zeros((h, w), np.uint8); cv2.fillPoly(t, [np.array(poly, np.int32) * UP], 255); bad |= t > 0
    keep = [p for p in cut_inside(keep, bad) if plen(p) >= 14]
    sil = cut_inside(outline(mask, cfg), bad) if bad.any() else outline(mask, cfg)
    for wh in wheels:
        if wh['tyre_arcs']:
            sil = cut_keep(sil, lambda p, T=wh['tyre']: ~inside_ellipse(T, p, 1.07), minlen=6)

    W_OUT, W_IN = cfg.get('w_out', 3.4), cfg.get('w_in', 2.5)
    a = render((h, w), [(p, W_OUT) for p in sil + wheel_strokes] + [(p, W_IN) for p in keep + plate_strokes])
    if cfg.get('fade'):
        low = np.zeros((h, w), np.float32); low[int(cfg['sill'] * UP):, :] = 1
        low = cv2.GaussianBlur(low, (0, 0), 12)
        a *= (1 - low) + low * np.clip(dist / 46.0, 0, 1)
    if cfg.get('fadeleft'):
        ramp = np.clip(np.arange(w) / float(cfg['fadeleft'] * UP), 0, 1) ** 1.4
        a *= ramp[None, :]

    ys, xs = np.where(mask > 0); pad = 24
    Y0, Y1 = max(0, ys.min() - pad), min(h, ys.max() + pad)
    X0, X1 = max(0, xs.min() - pad), min(w, xs.max() + pad)
    al = (np.clip(a, 0, 1) * 255).astype(np.uint8)[Y0:Y1, X0:X1]
    rgba = np.zeros(al.shape + (4,), np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = NAVY[2], NAVY[1], NAVY[0]
    rgba[..., 3] = al
    cv2.imwrite(f'/home/claude/kupage/ink2-{name}.png', rgba)
    ow, oh = int(X1 - X0), int(Y1 - Y0)
    d_out = ' '.join(svg_path(p, X0, Y0) for p in sil + wheel_strokes)
    d_in = ' '.join(svg_path(p, X0, Y0) for p in keep + plate_strokes)
    open(f'/home/claude/kupage/ink2-{name}.svg', 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ow} {oh}" fill="none" stroke="#14213D" '
        f'stroke-linecap="round" stroke-linejoin="round"><path stroke-width="{W_OUT}" d="{d_out}"/>'
        f'<path stroke-width="{W_IN}" d="{d_in}"/></svg>')
    if debug:
        prev = np.full(al.shape + (3,), (0xEC, 0xF6, 0xFA), np.float32)
        aa = al.astype(np.float32)[..., None] / 255.0
        prev = prev * (1 - aa) + np.array([0x3D, 0x21, 0x14], np.float32) * aa
        cv2.imwrite(f'/tmp/ref-{name}.png', cv2.resize(prev.astype(np.uint8), None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA))
    return dict(name=name, w=ow, h=oh, gamma=round(gamma, 2), strokes=len(keep))


if __name__ == '__main__':
    names = sys.argv[1:] or ALL
    for n in names:
        print(json.dumps(build(n)), flush=True)
