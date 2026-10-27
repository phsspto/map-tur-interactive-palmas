"""Extrai QUADRAS e AVENIDAS do PDF (código, sigla, posição e inclinação).

Uso:   python tools/3_extrair_quadras.py caminho/do/mapa.pdf [quadras.json]
Saída: quadras.json -> {"Q":[[codigo,sigla,x,y,angulo]...],"AV":[[nome,x,y,angulo]...]}
Esses dados são colados nas constantes QD e AVD de js/app.js.
Requer: pdfplumber.
"""
import pdfplumber,math,re,json,sys
pdf=pdfplumber.open(sys.argv[1]);pg=pdf.pages[0]
S=1316/pg.width;HP=pg.height
strs=[];cur=None
for ch in pg.chars:
    m=ch['matrix'];th=math.atan2(m[1],m[0]);ox,oy=m[4],m[5];u=math.hypot(m[0],m[1]);sz=u;adv=(ch.get('adv') or 0.5)*u
    c,s=math.cos(th),math.sin(th)
    if cur:
        dx,dy=ox-cur['ox'],oy-cur['oy'];t=dx*c+dy*s;pp=abs(-dx*s+dy*c)
        if abs(th-cur['th'])<0.035 and pp<0.35*sz and -0.2*sz<=t<=3*sz:
            cur['t'].append(ch['text']);cur['pts'].append((ox,oy,adv));cur['ox'],cur['oy']=ox,oy;continue
    cur={'th':th,'sz':sz,'t':[ch['text']],'pts':[(ox,oy,adv)],'ox':ox,'oy':oy};strs.append(cur)
out=[]
for s in strs:
    txt=''.join(s['t']).strip()
    if not txt:continue
    th=s['th'];c,s_=math.cos(th),math.sin(th);p=s['pts']
    x0,y0,_=p[0];x1,y1,a=p[-1];x1+=c*a;y1+=s_*a
    cx,cy=(x0+x1)/2-s_*(-0.35*s['sz'])*-1,(y0+y1)/2+c*0.35*s['sz']  # sobe meia altura de caixa
    cx=(x0+x1)/2-s_*0.35*s['sz'];cy=(y0+y1)/2+c*0.35*s['sz']
    out.append((txt,round(cx*S,1),round((HP-cy)*S,1),round(-math.degrees(th),1),s['sz']))
json.dump(out,open('strs.json','w'),ensure_ascii=False)
print(len(out))
code=re.compile(r'^(AE|AV)?\s?(\d{3,4})\s?([NS])$');sig=re.compile(r'^\((.+)\)$')
codes=[o for o in out if code.match(o[0])];sigs=[o for o in out if sig.match(o[0])]
print('codes',len(codes),'sigs',len(sigs))
ave=[o for o in out if re.match(r'^(Av\. ?(NS|LO) ?\d+B?( \(Av\.Parque\))?|Av\. ?JK|Av\. ?THEOTÔNIO SEGURADO|TO-\d+)$',o[0])]
print('avenidas',len(ave));print([o[0] for o in out if o[0].startswith('Av')][:10])
print(codes[:3],sigs[:3],ave[:3])

import collections
out=json.load(open('strs.json'))
code=re.compile(r'^(AE|AV)?\s?(\d{3,4})\s?([NS])$');comb=re.compile(r'^(AE|AV)?\s?(\d{3,4})\s?([NS])\s*\((.+)\)$');sig=re.compile(r'^\((.+)\)$')
Q=[];usedsig=set();rest=[]
sigs=[(i,o) for i,o in enumerate(out) if sig.match(o[0])]
for i,o in enumerate(out):
    m=code.match(o[0]);mc=comb.match(o[0])
    if mc:
        pre,num,h,sg=mc.groups();Q.append([((pre+' ') if pre else '')+num+' '+h,sg.strip(),o[1],o[2],o[3]]);continue
    if not m:continue
    pre,num,h=m.groups();best=None;bd=99
    for j,s in sigs:
        if j in usedsig:continue
        d=math.hypot(s[1]-o[1],s[2]-o[2])
        if d<bd and d<14:bd,best=d,(j,s)
    if best:
        usedsig.add(best[0]);s=best[1];Q.append([((pre+' ') if pre else '')+num+' '+h,sig.match(s[0]).group(1),round((o[1]+s[1])/2,1),round((o[2]+s[2])/2,1),o[3]])
    else:rest.append(o)
print('quadras',len(Q),'sem sigla',len(rest),rest[:5],'siglas sobrando',len([1 for j,s in sigs if j not in usedsig]))
print(collections.Counter(round(q[4]) for q in Q))
# dedupe por proximidade e codigo
ded=[]
for q in Q:
    if any(math.hypot(q[2]-d[2],q[3]-d[3])<8 for d in ded):continue
    ded.append(q)
print('dedup',len(ded))
AV=[]
rx=re.compile(r'^(Av\. ?(NS|LO) ?\d+B?( \(Av\.Parque\))?|Av\. ?JK|Av\. ?THEOTÔNIO SEGURADO|TO-\d+)$')
for o in out:
    if rx.match(o[0]):
        n=re.sub(r'Av\.(?=\S)','Av. ',o[0])
        if not any(a[0]==n and math.hypot(a[1]-o[1],a[2]-o[2])<8 for a in AV):AV.append([n,o[1],o[2],o[3]])
print('avenidas',len(AV),sorted(set(a[0] for a in AV)))
json.dump({'Q':ded,'AV':AV},open(sys.argv[2] if len(sys.argv)>2 else 'quadras.json','w'),ensure_ascii=False,separators=(',',':'))
print(len(json.dumps({'Q':ded,'AV':AV},ensure_ascii=False,separators=(',',':'))))
