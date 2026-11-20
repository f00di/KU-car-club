"""Third KU Car Club board: the hero tiles carry ink-line drawings traced from the
club's own Supra and Mustang photos (made by ink.py), on dotted paper."""
import json, re

# reuse the rough-stroke helpers from geom.py without running its build step
gsrc = open('/home/claude/kupage/geom.py').read()
exec(gsrc[:gsrc.index("res={'stage'")])

src = open('/home/claude/palettes/project/CarClub.dc.html').read()
S = json.load(open('/home/claude/kupage/sketch.json'))
INK = {'supra': '/_blob/58d0d2444f180d3923e6c26993a1055c', 'mustang': '/_blob/25d746ae14246161537b89729effe099'}
DIM = {'supra': (1541, 728), 'mustang': (1393, 563)}

ground = rough([(6, 7), (994, 7.6)], seed=31, amp=1.2, passes=2, closed=False, step=9, overshoot=0, off=0.8)
curl = lambda cls: (f'<svg class="curl {cls}" viewBox="0 0 120 80" aria-hidden="true" focusable="false">'
                    f'<path d="{S["curl"]}"></path></svg>')


def inkbox(k, cls, alt):
    w, h = DIM[k]
    return (f'<div class="ink {cls}">'
            f'<img src="{INK[k]}" alt="{alt}" width="{w}" height="{h}" decoding="async">'
            f'<svg class="ink-ground" viewBox="0 0 1000 14" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
            f'<path pathLength="1" d="{ground}"></path></svg></div>')


tileA = f'''<div class="tile t-carA t-ink">
{inkbox('supra', 'ink-a', "Ink-line drawing of a member's grey Toyota GR Supra, traced from a club photo")}
</div>
'''
tileB = f'''<div class="tile t-carB t-ink" id="explore">
{inkbox('mustang', 'ink-b', "Ink-line drawing of a member's Ford Mustang from its left side, traced from a club photo")}
</div>
'''
h = re.sub(r'<div class="tile t-carA">.*?</div>\n', tileA, src, count=1, flags=re.S)
h = re.sub(r'<div class="tile t-carB" id="explore">.*?</div>\n', tileB, h, count=1, flags=re.S)

CSS = '''
.t-ink{background-color:var(--ivory);background-image:radial-gradient(rgba(20,33,61,.13) 1px,transparent 1.4px);background-size:22px 22px}
.ink{position:absolute;transition:transform 900ms cubic-bezier(.23,1,.32,1)}
.ink img{display:block;width:100%;height:100%;animation:kuWipeR 1500ms cubic-bezier(.77,0,.175,1) 380ms backwards}
.ink-a img{animation-name:kuWipeL}
.ink-ground{position:absolute;left:-6%;width:112%;height:14px;overflow:visible}
.ink-ground path{fill:none;stroke:var(--navy);stroke-width:1.6;stroke-linecap:round;vector-effect:non-scaling-stroke;opacity:.75;stroke-dasharray:1;animation:kuDraw 900ms cubic-bezier(.77,0,.175,1) 1250ms backwards}
.ink-a{left:-11%;top:2%;width:111%;aspect-ratio:1541/728}
.ink-a .ink-ground{bottom:calc(3.3% - 2px)}
.ink-b{left:3%;top:4.5%;width:82%;aspect-ratio:1393/563}
.ink-b .ink-ground{display:none}
.sk-note{color:var(--navy);font-size:2.2cqw}
.ink-note-a{left:71%;top:7%}
.ink-curl-a{left:63%;top:12%;width:6cqw;height:4cqw;color:var(--navy);transform:scaleX(-1) rotate(-8deg)}
.ink-note-b{left:8%;top:30%}
.ink-curl-b{left:17%;top:41%;width:6cqw;height:4cqw;color:var(--navy);transform:rotate(14deg)}
@keyframes kuWipeR{from{clip-path:inset(0 100% 0 0)}to{clip-path:inset(0 0 0 0)}}
@keyframes kuWipeL{from{clip-path:inset(0 0 0 100%)}to{clip-path:inset(0 0 0 0)}}
[data-motion="false"] .ink img,[data-motion="false"] .ink-ground path{animation:none}
@media (prefers-reduced-motion:reduce){.ku .ink img,.ku .ink-ground path{animation:none}}
@media (hover:hover) and (pointer:fine){.t-ink:hover .ink-b{transform:translateX(-6px)}.t-ink:hover .ink-a{transform:translateX(6px)}}
@container ku (max-width:1100px){
.t-carA.t-ink{height:auto;aspect-ratio:2.14}
.ink-a{left:-2%;top:-3%;width:104%}
.ink-a .ink-ground{display:none}
.t-carB.t-ink{height:auto;aspect-ratio:2.55}
.ink-b{left:-2%;top:-4%;width:104%}
.sk-note{font-size:24px}.ink-curl-a,.ink-curl-b{display:none}
.ink-note-a,.ink-note-b{left:auto;right:24px;top:18px}
}
@container ku (max-width:640px){
.ink-ground{left:-3%;width:106%}
.sk-note{display:none}
}
'''
h = h.replace('</style>', CSS + '</style>', 1)
h = h.replace('<title>KU Car Club — Khalifa University car club, every car welcome</title>',
              '<title>KU Car Club — ink version</title>')
assert h.count('class="ink ') == 2 and 'kuWipeR' in h
open('/home/claude/palettes/project/CarClubInk.dc.html', 'w').write(h)
print('ok', len(h))
