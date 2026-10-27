"""Extrai os TEXTOS do PDF (posição, tamanho, cor, largura) e gera a camada de letras nítidas.

Uso:   python tools/2_extrair_textos.py caminho/do/mapa.pdf [textos.json]
Saída: textos.json e camada_texto.svg (o <svg id="tx"> que fica dentro de #stage no index.html).
Requer: pdfplumber.
"""
import pdfplumber,math,json,collections,re,sys,html
OUT_JSON=sys.argv[2] if len(sys.argv)>2 else 'textos.json'
pg=pdfplumber.open(sys.argv[1]).pages[0]
S=1316/pg.width;HP=pg.height
def col(c):
    if c is None:return '#000'
    c=tuple(c) if isinstance(c,(list,tuple)) else (c,)
    if len(c)==1:v=int(c[0]*255);return '#%02x%02x%02x'%(v,v,v)
    if len(c)==3:return '#%02x%02x%02x'%tuple(int(max(0,min(1,x))*255) for x in c)
    if len(c)==4:
        C,M,Y,K=c;r,g,b=[int(255*(1-min(1,x+K))) for x in (C,M,Y)];return '#%02x%02x%02x'%(r,g,b)
    return '#000'
G=[];cur=None
for ch in pg.chars:
    m=ch['matrix'];u=math.hypot(m[0],m[1]);th=math.atan2(m[1],m[0]);ox,oy=m[4],m[5];adv=(ch.get('adv') or .5)*u
    c,s=math.cos(th),math.sin(th);fc=col(ch.get('non_stroking_color'));fn=ch['fontname'];st=(fn,fc,round(u,2))
    if cur:
        dx,dy=ox-cur['ox'],oy-cur['oy'];t=dx*c+dy*s;pp=abs(-dx*s+dy*c)
        if abs(th-cur['th'])<0.035 and pp<0.35*u and -0.2*u<=t<=3*u and st==cur['st']:
            cur['t']+=ch['text'];cur['ox'],cur['oy'],cur['adv']=ox,oy,adv;continue
    cur={'th':th,'u':u,'st':st,'t':ch['text'],'x0':ox,'y0':oy,'ox':ox,'oy':oy,'adv':adv};G.append(cur)
fonts=collections.Counter();out=[]
for g in G:
    txt=g['t'];
    if not txt.strip():continue
    c,s=math.cos(g['th']),math.sin(g['th']);L=(g['ox']-g['x0'])*c+(g['oy']-g['y0'])*s+g['adv']
    fn=re.sub(r'^[A-Z]{6}\+','',g['st'][0]);fonts[(fn,g['st'][1])]+=1
    out.append({'t':txt,'x':round(g['x0']*S,2),'y':round((HP-g['y0'])*S,2),'r':round(-math.degrees(g['th']),1),'s':round(g['u']*S,2),'w':round(L*S,2),'f':fn,'c':g['st'][1]})
json.dump(out,open(OUT_JSON,'w'),ensure_ascii=False,separators=(',',':'))
print(len(out),'grupos');
for (f,c),n in fonts.most_common(30):print(n,f,c)
big=sorted(out,key=lambda o:-o['s'])[:8]
for o in big:print(o['s'],o['f'],o['c'],o['t'][:40])

T=json.load(open(OUT_JSON))
cls=lambda f:('S' if 'Swiss' in f else 'G' if 'Script' in f else 'K' if 'Black' in f else 'CB' if 'BoldCn' in f else 'C' if ('Cn' in f or 'Narrow' in f) else 'A')
parts=[]
for o in T:
    s=html.escape(o['t'].replace('\u00a0',' '),quote=False)
    tr=f' transform="rotate({o["r"]} {o["x"]} {o["y"]})"' if abs(o['r'])>0.05 else ''
    parts.append(f'<text class="{cls(o["f"])}" x="{o["x"]}" y="{o["y"]}" font-size="{o["s"]}" fill="{o["c"]}" textLength="{o["w"]}"{tr}>{s}</text>')
open('camada_texto.svg','w').write('<svg id="tx" viewBox="0 0 1316 922" aria-hidden="true">'+''.join(parts)+'</svg>')
print('camada_texto.svg gerada com',len(parts),'textos')
