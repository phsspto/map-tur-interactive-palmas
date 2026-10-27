"""Gera o FUNDO do mapa (sem textos, sem o logo do canto) a partir do PDF original.

Uso:   python tools/1_gerar_fundo.py caminho/do/mapa.pdf [saida.jpg]
Requer: pikepdf, poppler-utils (comando pdftoppm).

O que faz:
  1. Remove todos os textos do PDF (eles voltam como camada vetorial nítida em index.html, id="tx").
  2. Apaga as imagens minúsculas das bandeiras da pipa e do HGP (as bandeiras novas são desenhadas em SVG).
  3. Remove o logo "Cidade de Palmas" do canto superior direito (formas vetoriais naquela região).
  4. Renderiza em 4800 px de largura.
ATENÇÃO: os números dos objetos de imagem (785, 787, 502, 795, 800) valem para ESTE PDF.
Se o PDF mudar, é preciso descobrir os novos números (veja docs/COMO_FOI_FEITO.md).
"""
import sys,os,subprocess,tempfile
SRC=sys.argv[1];OUT=sys.argv[2] if len(sys.argv)>2 else 'mapa-fundo.jpg';TMP=tempfile.mkdtemp()
# ---- passo 1 e 2: remover textos e imagens das bandeiras ----
import pikepdf
src=SRC
pdf=pikepdf.open(src);seen=set();cnt=[0]
TEXTOPS={'BT','ET','Tc','Tw','Tz','TL','Tf','Tr','Ts','Td','TD','Tm','T*','Tj','TJ',"'",'"'}
def strip_ops(ops):
    new=[]
    for operands,op in ops:
        o=str(op)
        if o=='BT':cnt[0]+=1
        if o in TEXTOPS:continue
        new.append((operands,op))   # mantem cs/scn/gs etc. que ficavam dentro dos blocos de texto
    return new
def forms(res):
    out=[]
    if res is None:return out
    xo=res.get('/XObject')
    if xo is not None:
        for k in xo.keys():
            x=xo[k]
            if x.get('/Subtype')=='/Form':out.append(x)
    return out
def do_form(x):
    if x.objgen in seen:return
    seen.add(x.objgen)
    ops=pikepdf.parse_content_stream(x);x.write(pikepdf.unparse_content_stream(strip_ops(ops)))
    for f in forms(x.get('/Resources')):do_form(f)
# BLANK: apaga (deixa transparentes) as 3 imagens minusculas da bandeira da pipa, quadra 301 N
for og in [(785,0),(787,0),(502,0),(795,0),(800,0)]:
    x=pdf.get_object(og);sm=x.SMask;sm.write(bytes(int(sm.Width)*int(sm.Height)));print('apagada',og,int(sm.Width),int(sm.Height),sm.get('/BitsPerComponent'))
pg=pdf.pages[0]
ops=pikepdf.parse_content_stream(pg);pg.Contents=pdf.make_stream(pikepdf.unparse_content_stream(strip_ops(ops)))
for f in forms(pg.get('/Resources')):do_form(f)
pdf.save(TMP+'/notext.pdf');print('blocos BT removidos:',cnt[0],'forms:',len(seen))

# ---- passo 3: remover o logo do canto ----
import pikepdf,math
from pikepdf import Name
pdf=pikepdf.open(TMP+'/notext.pdf');pg=pdf.pages[0]
HP=float(pg.MediaBox[3])-float(pg.MediaBox[1]);WP=float(pg.MediaBox[2])-float(pg.MediaBox[0]);S=1316/WP
# região do logo (px do mapa, topo-esquerda) -> espaço PDF (y para cima)
RX0,RX1=1100/S,1252/S;RY0,RY1=HP-148/S,HP+12/S
def mul(A,B):
    a1,b1,c1,d1,e1,f1=A;a2,b2,c2,d2,e2,f2=B
    return [a1*a2+b1*c2,a1*b2+b1*d2,c1*a2+d1*c2,c1*b2+d1*d2,e1*a2+f1*c2+e2,e1*b2+f1*d2+f2]
def tp(M,x,y):return (x*M[0]+y*M[2]+M[4],x*M[1]+y*M[3]+M[5])
PAINT={'f','F','f*','B','B*','b','b*','S','s'};PATHOP={'m','l','c','v','y','h','re'}
removed=[0];seen=set()
def inregion(pts):
    if not pts:return False
    xs=[p[0] for p in pts];ys=[p[1] for p in pts]
    return min(xs)>=RX0-2 and max(xs)<=RX1+2 and min(ys)>=RY0-2 and max(ys)<=RY1+2 and (max(xs)-min(xs))<400
def run(obj,ctm,res):
    ops=pikepdf.parse_content_stream(obj);out=[];stack=[];buf=[];pts=[];clip=False
    for operands,op in ops:
        o=str(op)
        if o=='q':stack.append(list(ctm))
        elif o=='Q':
            if stack:ctm=stack.pop()
        elif o=='cm':ctm=mul([float(x) for x in operands],ctm)
        if o in PATHOP:
            v=[float(x) for x in operands]
            if o in('m','l'):pts.append(tp(ctm,v[0],v[1]))
            elif o=='c':pts+= [tp(ctm,v[0],v[1]),tp(ctm,v[2],v[3]),tp(ctm,v[4],v[5])]
            elif o in('v','y'):pts+=[tp(ctm,v[0],v[1]),tp(ctm,v[2],v[3])]
            elif o=='re':
                x,y,w,h=v;pts+=[tp(ctm,x,y),tp(ctm,x+w,y),tp(ctm,x,y+h),tp(ctm,x+w,y+h)]
            buf.append((operands,op));continue
        if o in('W','W*'):clip=True;buf.append((operands,op));continue
        if o in PAINT or o=='n':
            if o in PAINT and not clip and inregion(pts):removed[0]+=1   # descarta o desenho inteiro deste caminho
            else:out+=buf+[(operands,op)]
            buf=[];pts=[];clip=False;continue
        if buf:out+=buf;buf=[]   # operador inesperado no meio de um caminho: preserva
        out.append((operands,op))
        if o=='Do':
            xo=(res or {}).get('/XObject') if res is not None else None
            nm=operands[0]
            if xo is not None and nm in xo:
                x=xo[nm]
                if x.get('/Subtype')=='/Form' and x.objgen not in seen:
                    seen.add(x.objgen);m=x.get('/Matrix');M=[float(a) for a in m] if m is not None else [1,0,0,1,0,0]
                    run(x,mul(M,ctm),x.get('/Resources') or res)
    out+=buf
    data=pikepdf.unparse_content_stream(out)
    if isinstance(obj,pikepdf.Page) or obj is pg:obj.Contents=pdf.make_stream(data)
    else:obj.write(data)
run(pg,[1,0,0,1,0,0],pg.get('/Resources'))
pdf.save(TMP+'/notext2.pdf');print('caminhos removidos na região do logo:',removed[0])

base=os.path.join(TMP,'mapa')
subprocess.run(['pdftoppm','-jpeg','-jpegopt','quality=84','-scale-to-x','4800','-scale-to-y','-1','-singlefile',TMP+'/notext2.pdf',base],check=True)
os.replace(base+'.jpg',OUT);print('Fundo gerado em',OUT)
