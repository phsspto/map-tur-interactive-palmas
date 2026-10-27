# Ferramentas (opcionais)

Só são necessárias se o **PDF do mapa mudar** ou se você quiser refazer o fundo/textos. O site funciona sem elas.

Requisitos: Python 3, `pip install pikepdf pdfplumber pillow` e o `pdftoppm` (pacote *poppler-utils*).

| Script | O que gera | Onde usar |
|---|---|---|
| `1_gerar_fundo.py mapa.pdf` | `mapa-fundo.jpg` (sem textos, sem o logo do canto, 4800 px) | substitui `assets/mapa-fundo.jpg` |
| `2_extrair_textos.py mapa.pdf` | `textos.json` e `camada_texto.svg` | o `<svg id="tx">` dentro de `#stage` em `index.html` |
| `3_extrair_quadras.py mapa.pdf` | `quadras.json` (quadras e avenidas) | constantes `QD` e `AVD` em `js/app.js` |

Observações:
- `1_gerar_fundo.py` usa números de objetos específicos **deste** PDF (imagens das bandeiras da pipa e do HGP, região do logo). Com outro PDF, ajuste a lista e a região no próprio script (veja o cabeçalho dele).
- A quadra **101 S** não tem sigla no mapa e foi acrescentada à mão em `QD`.
- As bandeiras da pipa e do HGP em `index.html` (`<g id="flagpipa">` e `<g id="flaghgp">`) são desenhos SVG feitos à parte.
- Testado: os três scripts reproduzem exatamente o fundo (diferença 0), os 561 textos e as 203 quadras / 81 rótulos de avenidas usados hoje.
