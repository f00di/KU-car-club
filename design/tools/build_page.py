import json, html
G=json.load(open('geom.json'))['tiles']; S=json.load(open('sketch.json'))
B={'three':'/_blob/8dda13b35683dd0d56694395ed7d6616','coupes':'/_blob/3db7ed065e48fb3afce454e78608653e',
   'wm':'/_blob/b4c44acae566911423f1c09a5cdedbad','wmc':'/_blob/ed9c111215776ba102ea5e838bae70ea','badge':'/_blob/d4c214670947c40a3265a5f24526acb0',
   'pgt':'/_blob/94f028a7bca6eacf663df7ebac316a0a','pmc':'/_blob/5f4b9092fbbb5796374cdc53fe417e31','supra':'/_blob/9d3b032bacd19a5f4e935c0aaa28e830','mustang':'/_blob/a751dbd6cead9592d4d8a4da38a85928','supraGrey':'/_blob/d8bf2019eca390d5773cbd8f109281e3'}
PH={'P01':'fecc37d8108892c6aa0b2ec2cbff55f4','P04':'a238f70570d0fefe84bdd41712d5a896','P07':'c84b12620e7c06ff7d84f0c3be3aea0f','P08':'8ca868067aa9ebb6a68be9a4c60b1705','P09':'0b83259f9b349dff294d3299eb0e0c8e','P12':'1ba00f138cb8f8de78afeebe2ae36b37','P13':'8b3854420862a1d3582f93e5a7531259','P15':'a82963bca6d6e79179104b5d2931727c','P16':'6e17308b06bb1ccc5f85750a55dabaf7'}
FILMS=[('P01','Night meet','Night meet','Lights on, doors up.','A green coupe with scissor doors up and green underglow at a night meet'),
 ('P04','Our people','Our people','Come for the cars, stay for the people.','Members talking beside a light-blue sports car at night'),
 ('P07','Coffee & cars','Coffee and cars','A cup on the deck, the engine still ticking.','A coffee cup resting on the boot of a black convertible beside its red tail light'),
 ('P08','Line-up','The line-up','Parked nose to tail under the floodlights.','A row of sports cars parked at night, a white one in front'),
 ('P09','Classics','Classics','Small car, big welcome.','A red classic hatchback with round headlights at an evening meet'),
 ('P12','Wraps','Wraps','Paint, vinyl and a lot of patience.','A white coupe with a red and black art wrap and red wheels'),
 ('P13','Rare finds','Rare finds','The one everyone walks over to.','A dark blue pop-up headlight coupe parked at night'),
 ('P15','Details','Details','Carbon, vents and plates up close.','Close-up of the rear vents and carbon wing of an orange supercar'),
 ('P16','Supercars','Supercars','Parked next to a hatchback. Everyone is welcome.','An orange mid-engine supercar from behind at a crowded night meet')]
films_js=json.dumps([{'src':'/_blob/'+PH[p],'label':lab,'title':t,'cap':c,'alt':a} for p,lab,t,c,a in FILMS], ensure_ascii=False)

def pct(k):
    l,t,w,h=G[k]['pct']; return f"left:{l}%;top:{t}%;width:{w}%;height:{h}%"
def sk(name, cls='sk', vb=None, pl=False):
    vbs={'pill':'0 0 300 56','btn':'0 0 200 56','btnPill':'0 0 200 56','ring':'0 0 56 56','frame':'0 0 200 340','underline':'0 0 300 24','curl':'0 0 120 80','dash':'0 0 120 12','oval':'0 0 200 80'}
    v=vb or vbs.get(name,'0 0 48 48')
    par='' if v=='0 0 48 48' and cls=='ico' else ' preserveAspectRatio="none"'
    if name in ('curl',): par=''
    plen=' pathLength="1"' if pl else ''
    return f'<svg class="{cls}" viewBox="{v}"{par} aria-hidden="true" focusable="false"><path{plen} d="{S[name]}"></path></svg>'

clip_ids={'title':'kuClipTitle','carA':'kuClipA','carB':'kuClipB','meet':'kuClipMeet'}
defs=''.join(f'<clipPath id="{clip_ids[k]}" clipPathUnits="objectBoundingBox"><path d="{G[k]["clip"]}"></path></clipPath>' for k in clip_ids)
sketch_paths=''.join(f'<path pathLength="1" d="{G[k]["sketch"]}"></path>' for k in ('title','carA','carB','meet'))

CSS = r"""
body{margin:0}
a{color:inherit}
.ku{--navy:#14213D;--cream:#F3EBD8;--ivory:#FAF6EC;min-height:100vh;box-sizing:border-box;background:var(--cream);color:var(--navy);font-family:'Barlow',system-ui,sans-serif;container-type:inline-size;container-name:ku}
.ku *{box-sizing:border-box}
.ku-defs{position:absolute;width:0;height:0;overflow:hidden}
.sk{position:absolute;left:-5px;top:-5px;width:calc(100% + 10px);height:calc(100% + 10px);overflow:visible;pointer-events:none;transition:transform 220ms cubic-bezier(.23,1,.32,1)}
.sk path,.ico path,.ul path,.curl path{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
.ico{width:26px;height:26px;flex:none;overflow:visible}
.ku-nav{height:88px;display:flex;align-items:center;gap:24px;padding:0 40px}
.ku-logo{display:block;line-height:0;margin-right:auto;border-radius:8px}
.ku-logo img{height:64px;width:auto;display:block}
.ku-menu{position:relative;display:flex;gap:2px;padding:6px 10px}
.ku-menu .sk{color:var(--navy)}
.ku-menu a{position:relative;padding:10px 16px;font-size:16px;font-weight:600;text-decoration:none;border-radius:999px;transition:background-color 200ms ease}
.btn{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:0 22px;border-radius:999px;font:inherit;font-size:16px;font-weight:600;line-height:1;text-decoration:none;white-space:nowrap;cursor:pointer;border:0;background:transparent;color:inherit;transition:transform 160ms cubic-bezier(.23,1,.32,1),background-color 200ms ease}
.btn:active{transform:scale(.97)}
.btn-navy{background:var(--navy);color:var(--cream)}
.btn-navy .sk{color:var(--navy)}
.btn-cream{background:var(--cream);color:var(--navy)}
.btn-cream .sk{color:var(--cream)}
.btn-ghost{color:var(--cream)}
.btn-ghost .sk{color:var(--cream)}
.btn:focus-visible,.ku-menu a:focus-visible,.ku-logo:focus-visible,.arrow:focus-visible,.dot:focus-visible,.card:focus-visible,.meet-link:focus-visible{outline:2px solid currentColor;outline-offset:5px}
.ku-hero{padding:4px 40px 36px}
.ku-stage{position:relative;width:100%;aspect-ratio:1360 / 740;container-type:inline-size;container-name:stage}
.tile{position:absolute;overflow:hidden}
.t-title{%TITLE%;clip-path:url(#kuClipTitle);background:var(--navy);color:var(--cream)}
.t-carA{%CARA%;clip-path:url(#kuClipA);background:var(--ivory)}
.t-carB{%CARB%;clip-path:url(#kuClipB);background:var(--ivory)}
.t-meet{%MEET%;clip-path:url(#kuClipMeet);background:var(--navy);color:var(--cream)}
.ku-sketch{position:absolute;inset:0;width:100%;height:100%;pointer-events:none;overflow:visible;color:var(--navy)}
.ku-sketch path{fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:0}
.tt{position:absolute;inset:0;padding:2.5cqw 2.6cqw 2.4cqw;display:flex;flex-direction:column;gap:1cqw}
.h1{margin:0;display:flex;flex-direction:column;align-items:flex-start;gap:.5cqw}
.h1-a{font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:3.75cqw;line-height:.95;text-transform:uppercase;max-width:42cqw;text-wrap:balance}
.h1-b{position:relative;font-family:'Caveat',cursive;font-weight:700;font-size:3.1cqw;line-height:1;padding-right:.3cqw}
.ul{position:absolute;left:-2%;bottom:-1cqw;width:106%;height:1.5cqw;overflow:visible;pointer-events:none}
.h1-b .ul path{stroke-dasharray:1;stroke-dashoffset:0}
.tt-row{display:flex;gap:1.6cqw;align-items:flex-start;margin-top:auto;max-width:43cqw}
.tt-thumb{width:7.6cqw;height:7.6cqw;flex:none;border-radius:50%;display:block}
.tt-copy{display:flex;flex-direction:column;gap:1.1cqw}
.tt-copy p{margin:0;font-size:1.13cqw;line-height:1.45;color:rgba(243,235,216,.86)}
.tt-ctas{display:flex;gap:.9cqw;flex-wrap:wrap}
.tt .btn{min-height:3.3cqw;padding:0 1.6cqw;font-size:1.13cqw}
.car-photo{position:absolute;inset:0;width:100%;height:100%;display:block;object-fit:cover;transition:transform 700ms cubic-bezier(.23,1,.32,1)}
.t-carA .car-photo{object-position:50% 70%}
.t-carB .car-photo{object-position:50% 60%}
.note{position:absolute;margin:0;font-family:'Caveat',cursive;font-weight:700;line-height:.95;pointer-events:none}
.note-a{left:19.5%;top:7%;font-size:2.4cqw;color:var(--navy)}
.curl{position:absolute;overflow:visible;pointer-events:none}
.curl-a{left:21%;top:23%;width:8.8cqw;height:5.9cqw;color:var(--navy)}
.note-b{left:2.6%;top:8%;font-size:2.4cqw;display:flex;flex-direction:column;gap:.2cqw}
.note-b .ico{width:2.6cqw;height:2.6cqw;margin-bottom:.4cqw}
.curl-b{left:15%;top:38%;width:7.4cqw;height:5cqw;transform:rotate(-8deg)}
.spin{position:absolute;display:flex;align-items:center;gap:.4cqw;margin:0;font-family:'Caveat',cursive;font-weight:700;font-size:1.65cqw;pointer-events:none}
.spin .ico{width:1.8cqw;height:1.8cqw}
.spin-a{left:80%;top:5%}
.spin-b{left:66%;top:83%}
.tags{position:absolute;left:2.6%;bottom:8%;display:flex;flex-wrap:wrap;gap:.8cqw .7cqw;max-width:20cqw;margin:0;padding:0;list-style:none}
.tags li{position:relative;padding:.4cqw .95cqw;font-size:1cqw;font-weight:600;line-height:1.2}
.tags li .sk{left:-3px;top:-3px;width:calc(100% + 6px);height:calc(100% + 6px)}
.meet-ico{position:absolute;left:79%;top:8%;width:3.4cqw;height:3.4cqw}
.meet-note{position:absolute;left:47%;top:13%;margin:0;font-family:'Caveat',cursive;font-weight:700;font-size:1.7cqw;transform:rotate(-7deg);color:var(--cream)}
.meet-body{position:absolute;left:30%;top:45%;right:7%;display:flex;flex-direction:column;gap:.55cqw}
.meet-body h2{margin:0;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:2.3cqw;line-height:.95;text-transform:uppercase}
.meet-body p{margin:0;font-size:1.02cqw;line-height:1.4;color:rgba(243,235,216,.86)}
.meet-link{position:relative;align-self:flex-start;display:inline-flex;align-items:center;gap:.4cqw;margin-top:.3cqw;font-size:1.08cqw;font-weight:600;text-decoration:none;padding:.3cqw 0}
.meet-link .ul{bottom:-.5cqw;height:1cqw}
.meet-link .ico{width:1.6cqw;height:1.6cqw}
.ku-film{background:var(--navy);color:var(--cream);padding:84px 0 56px;overflow:hidden}
.film-head{display:flex;flex-direction:column;align-items:center;gap:16px;text-align:center;padding:0 40px}
.film-over{margin:0;display:flex;align-items:center;gap:14px;font-size:12px;font-weight:600;letter-spacing:.24em;text-transform:uppercase;color:#E9DDBF}
.film-over svg{position:static;width:64px;height:10px}
.film-h2{margin:0;font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:64px;line-height:1;letter-spacing:-.005em}
.film-h2 em{position:relative;font-family:'Instrument Serif',serif;font-style:italic;font-weight:400;font-size:1.08em}
.film-h2 em .ul{bottom:-6px;height:14px}
.film-sub{margin:0;font-size:16px;color:rgba(243,235,216,.82)}
.reel{position:relative;height:440px;margin-top:34px;perspective:860px;perspective-origin:50% 50%;overflow:hidden;touch-action:pan-y;cursor:grab;user-select:none;--R:700px;--step:15.3deg;--cw:186px;--ch:308px}
.reel.dragging{cursor:grabbing}
.drum{position:absolute;left:50%;top:50%;width:0;height:0;transform-style:preserve-3d;transition:transform 700ms cubic-bezier(.23,1,.32,1)}
.reel.dragging .drum{transition:none}
.card{position:absolute;left:calc(var(--cw) / -2);top:calc(var(--ch) / -2);width:var(--cw);height:var(--ch);padding:0;border:0;border-radius:14px;background:transparent;color:var(--cream);font:inherit;text-align:left;cursor:pointer;backface-visibility:hidden}
.card img{position:absolute;left:9px;top:9px;width:calc(100% - 18px);height:calc(100% - 18px);object-fit:cover;border-radius:10px;display:block;filter:saturate(.85) brightness(.78);transition:filter 300ms ease;pointer-events:none}
.card::after{content:'';position:absolute;inset:9px;border-radius:10px;background:linear-gradient(to top,rgba(10,16,32,.86),rgba(10,16,32,0) 46%);pointer-events:none}
.card.on img{filter:none}
.card.far{visibility:hidden}
.card-no{position:absolute;left:21px;top:19px;z-index:1;font-size:11px;font-weight:600;letter-spacing:.08em}
.card-label{position:absolute;left:21px;bottom:21px;right:57px;z-index:1;font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:21px;line-height:1}
.card .frame{position:absolute;left:0;top:0;width:100%;height:100%;overflow:visible;pointer-events:none;color:var(--cream);z-index:2}
.card .frame path{fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}
.card-play{position:absolute;right:19px;bottom:18px;z-index:1;width:32px;height:32px;display:grid;place-items:center;color:var(--cream)}
.card-play .ico{width:22px;height:22px}
.card-play .sk{left:0;top:0;width:100%;height:100%}
.drag-hint{margin:14px 0 0;text-align:center;font-family:'Caveat',cursive;font-weight:700;font-size:22px;color:#E9DDBF}
.film-foot{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:24px;max-width:1360px;margin:18px auto 0;padding:22px 40px 0;position:relative}
.film-foot::before{content:'';position:absolute;left:40px;right:40px;top:0;height:1px;background:rgba(243,235,216,.2)}
.counter{margin:0;display:flex;align-items:baseline;gap:8px}
.counter b{font-family:'Instrument Serif',serif;font-weight:400;font-size:60px;line-height:1}
.counter span{font-size:14px;color:rgba(243,235,216,.72)}
.film-cap{text-align:center}
.film-cap h3{margin:0;font-family:'Barlow Condensed',sans-serif;font-weight:600;font-size:32px;line-height:1.05}
.film-cap p{margin:6px 0 0;font-size:15px;color:rgba(243,235,216,.82)}
.film-arrows{justify-self:end;display:flex;gap:12px}
.arrow{position:relative;width:54px;height:54px;border:0;padding:0;background:transparent;color:var(--cream);cursor:pointer;display:grid;place-items:center;transition:transform 160ms cubic-bezier(.23,1,.32,1),opacity 200ms ease}
.arrow .sk{left:0;top:0;width:100%;height:100%}
.arrow .ico{width:24px;height:24px}
.arrow:active{transform:scale(.95)}
.arrow:disabled{opacity:.35;cursor:default}
.dots{display:flex;justify-content:center;gap:2px;margin-top:20px}
.dot{min-width:24px;height:28px;padding:0 6px;border:0;background:transparent;cursor:pointer;display:grid;place-items:center}
.dot i{display:block;width:8px;height:8px;border-radius:999px;background:rgba(243,235,216,.38);transition:width 300ms cubic-bezier(.23,1,.32,1),background-color 200ms ease}
.dot.on i{width:28px;background:var(--cream)}
@media (hover:hover) and (pointer:fine){
.btn:hover{transform:translateY(-2px)}
.btn:active{transform:scale(.97)}
.btn:hover .sk{transform:translate(2px,2px)}
.ku-menu a:hover{background:rgba(20,33,61,.08)}
.arrow:not(:disabled):hover{transform:translateY(-2px)}
.card:hover img{filter:none}
.t-carA:hover .car-photo,.t-carB:hover .car-photo{transform:scale(1.025)}
.meet-link:hover .ico{transform:translateX(3px)}
}
.meet-link .ico{transition:transform 200ms cubic-bezier(.23,1,.32,1)}
@keyframes kuIn{from{opacity:0;transform:translateY(14px) scale(.985)}}
@keyframes kuFade{from{opacity:0}}
@keyframes kuDraw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}
.tile{animation:kuIn 820ms cubic-bezier(.23,1,.32,1) backwards}
.t-carA{animation-delay:90ms}.t-carB{animation-delay:170ms}.t-meet{animation-delay:250ms}
.ku-sketch path{animation:kuDraw 1700ms cubic-bezier(.77,0,.175,1) 280ms backwards}
.h1-b .ul path{animation:kuDraw 900ms cubic-bezier(.77,0,.175,1) 900ms backwards}
.ku-nav{animation:kuFade 600ms ease backwards}
[data-motion="false"] .tile,[data-motion="false"] .ku-sketch path,[data-motion="false"] .ul path,[data-motion="false"] .ku-nav{animation:none}
@media (prefers-reduced-motion:reduce){.tile{animation-name:kuFade;animation-duration:300ms}.ku-sketch path,.ul path{animation:none}.drum{transition-duration:200ms}}
@container ku (max-width:1100px){
.ku-menu{display:none}
.ku-stage{aspect-ratio:auto;display:flex;flex-direction:column;gap:14px}
.tile{position:relative;left:auto;top:auto;width:100%;clip-path:none;border-radius:24px;border:2px solid var(--navy)}
.t-title,.t-meet{height:auto}
.t-carA,.t-carB{height:340px}
.ku-sketch{display:none}
.tt{position:relative;inset:auto;padding:28px;gap:14px}
.h1-a{font-size:46px;max-width:none}
.h1-b{font-size:38px}
.ul{bottom:-10px;height:14px}
.tt-row{max-width:none;margin-top:14px}
.tt-thumb{width:96px;height:96px}
.tt-copy{gap:14px}
.tt-copy p{font-size:16px}
.tt-ctas{gap:12px}
.tt .btn{min-height:46px;font-size:16px;padding:0 20px}
.note-a,.note-b{font-size:26px}
.note-b .ico{width:28px;height:28px}
.curl-a{display:none}
.t-carA .car-photo{object-position:50% 70%}
.t-carB .car-photo{object-position:28% 70%}
.spin{font-size:20px}.spin .ico{width:20px;height:20px}
.spin-a,.spin-b{left:auto;right:20px;top:auto;bottom:16px}
.tags{max-width:260px;gap:10px 8px}.tags li{font-size:13px;padding:5px 12px}
.meet-ico{left:auto;right:24px;top:24px;width:40px;height:40px}
.meet-note{left:auto;right:76px;top:30px;font-size:22px}
.meet-body{position:relative;left:auto;top:auto;right:auto;padding:28px;gap:8px}
.meet-body h2{font-size:34px}
.meet-body p{font-size:16px;max-width:30em}
.meet-link{font-size:16px}.meet-link .ico{width:20px;height:20px}
}
@container ku (max-width:640px){
.ku-nav{padding:0 20px;height:72px}
.ku-logo img{height:42px}
.ku-hero{padding:4px 20px 24px}
.t-carA,.t-carB{height:260px}
.h1-a{font-size:36px}
.h1-b{font-size:31px}
.tt{padding:22px}
.tt-row{flex-direction:column}
.tags{display:none}
.note-b{font-size:22px}
.film-head{padding:0 20px}
.film-h2{font-size:44px}
.reel{height:310px;perspective:540px;--R:430px;--step:17.7deg;--cw:132px;--ch:222px}
.card-label{font-size:17px}
.film-foot{grid-template-columns:1fr auto;padding:20px 20px 0}
.film-foot::before{left:20px;right:20px}
.film-cap{grid-column:1 / -1;order:-1;text-align:left}
.counter b{font-size:46px}
}
"""
CSS=CSS.replace('%TITLE%',pct('title')).replace('%CARA%',pct('carA')).replace('%CARB%',pct('carB')).replace('%MEET%',pct('meet'))

TAGS=['JDM','Euro','Muscle','4x4','Classics','Daily drivers']
tags_html=''.join(f'<li>{sk("btnPill")}{t}</li>' for t in TAGS)

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>KU Car Club — Khalifa University car club, every car welcome</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&amp;family=Barlow:wght@400;500;600&amp;family=Caveat:wght@500;700&amp;family=Instrument+Serif:ital@0;1&amp;display=swap" rel="stylesheet">
<style>{CSS}</style>
</helmet>
<div class="ku" data-motion="{{{{ motionAttr }}}}">
<svg class="ku-defs" width="0" height="0" aria-hidden="true" focusable="false"><defs>{defs}</defs></svg>
<header class="ku-nav">
<a class="ku-logo" href="#top"><img src="{B['wm']}" alt="KU Car Club"></a>
<nav class="ku-menu" aria-label="Main">
{sk('pill')}
<a href="#club">The club</a>
<a href="#explore">Explore UAE</a>
<a href="#people">Our people</a>
<a href="#next">Next meet</a>
</nav>
<a class="btn btn-navy" href="#join">{sk('btnPill')}Join free</a>
</header>
<main id="top" class="ku-hero">
<div class="ku-stage">
<section class="tile t-title" aria-labelledby="ku-h1">
<div class="tt">
<h1 class="h1" id="ku-h1"><span class="h1-a">Khalifa University’s car club</span><span class="h1-b">every car welcome{sk('underline','ul',pl=True)}</span></h1>
<div class="tt-row">
<img class="tt-thumb" src="{B['badge']}" alt="KU Car Club badge: an off-roader and a gear above the club name">
<div class="tt-copy">
<p>Student-run, backed by the Abu Dhabi Motor Majlis and free to join, no invite needed. Night meets, drives across the seven emirates, and room for whatever you drive.</p>
<div class="tt-ctas">
<a class="btn btn-cream" href="#join">{sk('btnPill')}Join the club</a>
<a class="btn btn-ghost" href="#next">{sk('btnPill')}See the next meet</a>
</div>
</div>
</div>
</div>
</section>
<div class="tile t-carA">
<img class="car-photo" src="{B['supraGrey']}" alt="A member's grey Toyota GR Supra with bronze wheels, parked at dusk">
</div>
<div class="tile t-carB" id="explore">
<img class="car-photo" src="{B['mustang']}" alt="A member's dark grey Ford Mustang with black stripes in a car park at dusk">
</div>
<aside class="tile t-meet" id="next" aria-labelledby="ku-next">
{sk('calendar','ico meet-ico')}
<div class="meet-body">
<h2 id="ku-next">Next meet</h2>
<p>Date and venue announced soon. Free entry, open to everyone.</p>
<a class="meet-link" href="#join">Get the meet alert{sk('arrowR','ico')}{sk('dash','ul')}</a>
</div>
</aside>
<svg class="ku-sketch" viewBox="0 0 1360 740" aria-hidden="true" focusable="false">{sketch_paths}</svg>
</div>
</main>
<section class="ku-film" id="club" aria-labelledby="ku-film-h">
<div class="film-head" id="people">
<p class="film-over">{sk('dash')}KU Car Club / The film collection{sk('dash')}</p>
<h2 class="film-h2" id="ku-film-h">The club, <em>in motion.{sk('underline','ul')}</em></h2>
<p class="film-sub">The places. The people. The nights worth showing up for.</p>
</div>
<div class="{{{{ reelCls }}}}" onPointerDown="{{{{ down }}}}" onPointerMove="{{{{ move }}}}" onPointerUp="{{{{ up }}}}" onPointerCancel="{{{{ up }}}}" onLostPointerCapture="{{{{ up }}}}">
<div class="drum" style="transform: {{{{ drumT }}}}">
<sc-for list="{{{{ cards }}}}" as="c" hint-placeholder-count="9">
<button class="card {{{{ c.cls }}}}" type="button" style="transform: {{{{ c.t }}}}" onClick="{{{{ c.pick }}}}" aria-label="{{{{ c.aria }}}}">
<img src="{{{{ c.src }}}}" alt="{{{{ c.alt }}}}" draggable="false">
<span class="card-no">{{{{ c.no }}}}</span>
<span class="card-label">{{{{ c.label }}}}</span>
<sc-if value="{{{{ c.active }}}}" hint-placeholder-val="{{{{ false }}}}">{sk('frame','frame')}<span class="card-play">{sk('ring')}{sk('play','ico')}</span></sc-if>
</button>
</sc-for>
</div>
</div>
<p class="drag-hint">drag to explore</p>
<div class="film-foot">
<p class="counter"><b>{{{{ counterNo }}}}</b><span>/ 09</span></p>
<div class="film-cap" aria-live="polite"><h3>{{{{ activeTitle }}}}</h3><p>{{{{ activeCap }}}}</p></div>
<div class="film-arrows">
<button class="arrow" type="button" aria-label="Previous film" onClick="{{{{ prev }}}}" disabled="{{{{ prevOff }}}}">{sk('ring')}{sk('arrowL','ico')}</button>
<button class="arrow" type="button" aria-label="Next film" onClick="{{{{ next }}}}" disabled="{{{{ nextOff }}}}">{sk('ring')}{sk('arrowR','ico')}</button>
</div>
</div>
<div class="dots">
<sc-for list="{{{{ dots }}}}" as="d" hint-placeholder-count="9"><button class="dot {{{{ d.cls }}}}" type="button" aria-label="{{{{ d.aria }}}}" onClick="{{{{ d.pick }}}}"><i></i></button></sc-for>
</div>
</section>
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"motion":{{"editor":"boolean","default":true,"section":"Motion"}},"$preview":{{"width":1440,"height":1800}}}}'>
class Component extends DCLogic {{
  constructor(props) {{
    super(props);
    this.state = {{ pos: 4, drag: false }};
    this._films = {films_js};
    var self = this;
    this._down = function (e) {{
      var w = e.currentTarget.clientWidth;
      self._ppc = w < 640 ? 132 : 186; self._x0 = e.clientX; self._p0 = self.state.pos; self._moved = 0; self._dragging = true;
      try {{ e.currentTarget.setPointerCapture(e.pointerId); }} catch (err) {{}}
      self.setState({{ drag: true }});
    }};
    this._move = function (e) {{
      if (!self._dragging) return;
      var dx = e.clientX - self._x0; self._moved = Math.max(self._moved, Math.abs(dx));
      var p = Math.max(-0.45, Math.min(8.45, self._p0 - dx / self._ppc));
      self.setState({{ pos: p }});
    }};
    this._up = function () {{
      if (!self._dragging) return;
      self._dragging = false;
      self.setState({{ drag: false, pos: Math.max(0, Math.min(8, Math.round(self.state.pos))) }});
    }};
    this._prev = function () {{ self.setState({{ pos: Math.max(0, Math.round(self.state.pos) - 1) }}); }};
    this._next = function () {{ self.setState({{ pos: Math.min(8, Math.round(self.state.pos) + 1) }}); }};
  }}
  renderVals() {{
    var s = this.state, self = this, p = this.props || {{}}, F = this._films;
    var pos = s.pos, act = Math.max(0, Math.min(8, Math.round(pos)));
    var cards = F.map(function (f, i) {{
      var d = Math.abs(i - pos);
      return {{
        src: f.src, alt: f.alt, label: f.label, no: '0' + (i + 1),
        t: 'rotateY(calc(var(--step) * ' + (-i) + ')) translateZ(calc(-1 * var(--R)))',
        cls: (i === act ? 'on' : '') + (d > 3.7 ? ' far' : ''), active: i === act,
        aria: 'Show ' + f.title,
        pick: function () {{ if (self._moved > 6) {{ self._moved = 0; return; }} self.setState({{ pos: i }}); }}
      }};
    }});
    var dots = F.map(function (f, i) {{
      return {{ cls: i === act ? 'on' : '', aria: 'Show ' + (i + 1) + ' of 9: ' + f.title, pick: function () {{ self.setState({{ pos: i }}); }} }};
    }});
    return {{
      motionAttr: String(p.motion === undefined ? true : p.motion),
      reelCls: 'reel' + (s.drag ? ' dragging' : ''),
      drumT: 'translateZ(var(--R)) rotateY(calc(var(--step) * ' + pos.toFixed(3) + '))',
      cards: cards, dots: dots,
      counterNo: '0' + (act + 1), activeTitle: F[act].title, activeCap: F[act].cap,
      down: this._down, move: this._move, up: this._up, prev: this._prev, next: this._next,
      prevOff: act === 0, nextOff: act === 8
    }};
  }}
}}
</script>
</body>
</html>
"""
open('/home/claude/palettes/project/CarClub.dc.html','w').write(HTML)
print(len(HTML))
