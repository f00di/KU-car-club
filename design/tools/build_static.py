import re, json, shutil, os
import sys
src=open(sys.argv[1] if len(sys.argv)>1 else '/home/claude/palettes/project/CarClub.dc.html').read()
OUT=sys.argv[2] if len(sys.argv)>2 else '/home/claude/kusite'
blob2file={'58d0d2444f180d3923e6c26993a1055c':'ink2-supra.png','25d746ae14246161537b89729effe099':'ink2-mustang.png','8dda13b35683dd0d56694395ed7d6616':'three.min.js','3db7ed065e48fb3afce454e78608653e':'ku-coupes.js',
 'b4c44acae566911423f1c09a5cdedbad':'ku-wordmark.png','ed9c111215776ba102ea5e838bae70ea':'ku-wordmark-cream.png','d4c214670947c40a3265a5f24526acb0':'ku-badge.png',
 '9d3b032bacd19a5f4e935c0aaa28e830':'ku-supra-night.webp','d8bf2019eca390d5773cbd8f109281e3':'ku-supra-grey.jpg','a751dbd6cead9592d4d8a4da38a85928':'ku-mustang.jpg',
 'fecc37d8108892c6aa0b2ec2cbff55f4':'ku-P01.jpg','a238f70570d0fefe84bdd41712d5a896':'ku-P04.jpg','c84b12620e7c06ff7d84f0c3be3aea0f':'ku-P07.jpg','8ca868067aa9ebb6a68be9a4c60b1705':'ku-P08.jpg','0b83259f9b349dff294d3299eb0e0c8e':'ku-P09.jpg','1ba00f138cb8f8de78afeebe2ae36b37':'ku-P12.jpg','8b3854420862a1d3582f93e5a7531259':'ku-P13.jpg','a82963bca6d6e79179104b5d2931727c':'ku-P15.jpg','6e17308b06bb1ccc5f85750a55dabaf7':'ku-P16.jpg'}
films=json.loads(re.search(r'this\._films = (\[.*?\]);\n', src).group(1))
h=src
for b,f in blob2file.items(): h=h.replace('/_blob/'+b, f)
for f in films: pass
films=[{**f,'src':f['src'].replace('/_blob/','')} for f in films]
for f in films:
    f['src']=blob2file.get(f['src'],f['src'])
# head
h=h.replace('<script src="./support.js"></script>\n','<meta name="viewport" content="width=device-width, initial-scale=1">\n')
helmet=re.search(r'<helmet>\n(.*?)\n</helmet>\n', h, re.S).group(1)
helmet=re.sub(r'<link href="https://fonts.googleapis.com[^>]*>', '', helmet)
h=h.replace('</head>', '''<style>
@font-face{font-family:'Barlow Condensed';font-weight:600;font-display:swap;src:url(fonts/BarlowCondensed-SemiBold.woff) format('woff')}
@font-face{font-family:'Barlow Condensed';font-weight:700;font-display:swap;src:url(fonts/BarlowCondensed-Bold.woff) format('woff')}
@font-face{font-family:'Barlow';font-weight:400;font-display:swap;src:url(fonts/Barlow-Regular.woff) format('woff')}
@font-face{font-family:'Barlow';font-weight:500;font-display:swap;src:url(fonts/Barlow-Medium.woff) format('woff')}
@font-face{font-family:'Barlow';font-weight:600;font-display:swap;src:url(fonts/Barlow-SemiBold.woff) format('woff')}
@font-face{font-family:'Caveat';font-weight:400 700;font-display:swap;src:url(fonts/Caveat-Variable.woff) format('woff')}
@font-face{font-family:'Instrument Serif';font-style:normal;font-weight:400;font-display:swap;src:url(fonts/InstrumentSerif-Regular.woff) format('woff')}
@font-face{font-family:'Instrument Serif';font-style:italic;font-weight:400;font-display:swap;src:url(fonts/InstrumentSerif-Italic.woff) format('woff')}
</style>'''+helmet+'\n</head>',1)
h=re.sub(r'<helmet>\n.*?\n</helmet>\n','',h,flags=re.S)
h=h.replace('<x-dc>\n','').replace('</x-dc>\n','')
h=h.replace('data-motion="{{ motionAttr }}"','data-motion="true" id="kuRoot"')
h=h.replace('<sc-if value="{{ showPosters }}" hint-placeholder-val="{{ true }}"><img class="car-poster" src="poster-gt.webp" alt=""></sc-if>','<img class="car-poster" id="posterA" src="poster-gt.webp" alt="">')
h=h.replace('<sc-if value="{{ showPosters }}" hint-placeholder-val="{{ true }}"><img class="car-poster" src="poster-mc.webp" alt=""></sc-if>','<img class="car-poster" id="posterB" src="poster-mc.webp" alt="">')
h=h.replace('ref="{{ refA }}"','id="carA"').replace('ref="{{ refB }}"','id="carB"')
h=re.sub(r'<div class="\{\{ reelCls \}\}"[^>]*>','<div class="reel" id="reel">',h)
h=h.replace('<div class="drum" style="transform: {{ drumT }}">','<div class="drum" id="drum" style="transform: translateZ(var(--R)) rotateY(calc(var(--step) * 4))">')
card_tpl=re.search(r'<sc-for list="\{\{ cards \}\}" as="c" hint-placeholder-count="9">\n(.*?)\n</sc-for>', h, re.S)
tpl=card_tpl.group(1)
frame_if=re.search(r'<sc-if value="\{\{ c\.active \}\}" hint-placeholder-val="\{\{ false \}\}">(.*?)</sc-if>', tpl, re.S).group(1)
cards=''
for i,f in enumerate(films):
    c=tpl
    c=re.sub(r'<sc-if value="\{\{ c\.active \}\}" hint-placeholder-val="\{\{ false \}\}">.*?</sc-if>', '<span class="active-only">'+frame_if+'</span>', c, flags=re.S)
    c=c.replace('class="card {{ c.cls }}"', f'class="card{" on" if i==4 else ""}" data-i="{i}"')
    c=c.replace('style="transform: {{ c.t }}"', f'style="transform: rotateY(calc(var(--step) * {-i})) translateZ(calc(-1 * var(--R)))"')
    c=c.replace(' onClick="{{ c.pick }}"','').replace('aria-label="{{ c.aria }}"', f'aria-label="Show {f["title"]}"')
    c=c.replace('src="{{ c.src }}"', f'src="{f["src"]}"').replace('alt="{{ c.alt }}"', f'alt="{f["alt"]}"')
    c=c.replace('{{ c.no }}', f'0{i+1}').replace('{{ c.label }}', f['label'].replace('&','&amp;'))
    cards+=c+'\n'
h=h.replace(card_tpl.group(0), cards)
h=h.replace('<b>{{ counterNo }}</b>','<b id="counter">05</b>').replace('<h3>{{ activeTitle }}</h3><p>{{ activeCap }}</p>',f'<h3 id="capTitle">{films[4]["title"]}</h3><p id="capText">{films[4]["cap"]}</p>')
h=h.replace('aria-label="Previous film" onClick="{{ prev }}" disabled="{{ prevOff }}"','aria-label="Previous film" id="prev"').replace('aria-label="Next film" onClick="{{ next }}" disabled="{{ nextOff }}"','aria-label="Next film" id="next"')
dots=''.join(f'<button class="dot{" on" if i==4 else ""}" type="button" data-i="{i}" aria-label="Show {i+1} of 9: {f["title"]}"><i></i></button>' for i,f in enumerate(films))
h=re.sub(r'<sc-for list="\{\{ dots \}\}".*?</sc-for>', dots, h, flags=re.S)
h=re.sub(r'<script type="text/x-dc" data-dc-script.*?</script>\n', '', h, flags=re.S)
assert '{{' not in h, re.findall(r'.{40}\{\{.{40}', h)[:3]
css_extra='.card .active-only{display:none}.card.on .active-only{display:block}\n'
h=h.replace('</style>', css_extra+'</style>',1)
films_js=json.dumps([{'title':f['title'],'cap':f['cap']} for f in films])
JS=r"""<script>
(function(){
  var F=%FILMS%, root=document.getElementById('kuRoot');
  // film reel
  var reel=document.getElementById('reel'), drum=document.getElementById('drum'), cards=[].slice.call(reel.querySelectorAll('.card')), dots=[].slice.call(document.querySelectorAll('.dot'));
  var pos=4, drag=false, x0=0, p0=0, moved=0, ppc=180;
  function render(){
    var act=Math.max(0,Math.min(8,Math.round(pos)));
    drum.style.transform='translateZ(var(--R)) rotateY(calc(var(--step) * '+pos.toFixed(3)+'))';
    cards.forEach(function(c,i){ c.classList.toggle('on',i===act); c.classList.toggle('far',Math.abs(i-pos)>3.7); });
    dots.forEach(function(d,i){ d.classList.toggle('on',i===act); });
    document.getElementById('counter').textContent='0'+(act+1);
    document.getElementById('capTitle').textContent=F[act].title; document.getElementById('capText').textContent=F[act].cap;
    document.getElementById('prev').disabled=act===0; document.getElementById('next').disabled=act===8;
  }
  reel.addEventListener('pointerdown',function(e){ ppc=reel.clientWidth<640?132:186; x0=e.clientX; p0=pos; moved=0; drag=true; reel.classList.add('dragging'); try{reel.setPointerCapture(e.pointerId);}catch(_){} });
  reel.addEventListener('pointermove',function(e){ if(!drag) return; var dx=e.clientX-x0; moved=Math.max(moved,Math.abs(dx)); pos=Math.max(-0.45,Math.min(8.45,p0-dx/ppc)); render(); });
  function up(){ if(!drag) return; drag=false; reel.classList.remove('dragging'); pos=Math.max(0,Math.min(8,Math.round(pos))); render(); }
  reel.addEventListener('pointerup',up); reel.addEventListener('pointercancel',up); reel.addEventListener('lostpointercapture',up);
  cards.forEach(function(c,i){ c.addEventListener('click',function(){ if(moved>6){moved=0;return;} pos=i; render(); }); });
  dots.forEach(function(d,i){ d.addEventListener('click',function(){ pos=i; render(); }); });
  document.getElementById('prev').addEventListener('click',function(){ pos=Math.max(0,Math.round(pos)-1); render(); });
  document.getElementById('next').addEventListener('click',function(){ pos=Math.min(8,Math.round(pos)+1); render(); });
  render();
})();
</script>
""".replace('%FILMS%',films_js)
h=h.replace('</body>', JS+'</body>')
open(OUT+'/index.html','w').write(h)
for f in set(blob2file.values()):
    shutil.copy(('/home/claude/kupage/' if f.startswith('ink') else '/home/claude/kupage/assets/')+('three-r159.min.js' if f=='three.min.js' else f), OUT+'/'+f) if f not in ('three.min.js','ku-coupes.js','poster-gt.webp','poster-mc.webp') else None
print('ok', len(h))
