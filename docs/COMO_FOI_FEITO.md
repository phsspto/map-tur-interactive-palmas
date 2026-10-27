# Como o mapa funciona (visão técnica)

## Camadas dentro de `#stage` (tudo na mesma escala do mapa, 1316 × 922 unidades)
1. `<img>` — `assets/mapa-fundo.jpg`, o PDF renderizado **sem textos**.
2. `#tint` — cor por hora do dia (`mix-blend-mode: multiply`).
3. `<svg id="tx">` — **letras nítidas** do PDF (561 textos, cada um com posição, tamanho, cor e largura exatos via `textLength`) e as bandeiras redesenhadas.
4. Camadas dinâmicas — contornos das quadras (`.q`), destaque amarelo (`.mk`) e os botões (`.pin`).

Zoom e arrasto: `translate/scale` no `#stage` (variáveis `S`, `X`, `Y`). Os botões são contra-escalados (`--inv`) para manter o tamanho.

## Dados
- Locais, categorias, marcadores, horários, cores etc. ficam no objeto `CFG` (salvo em `localStorage`, chave `palmas-map-cfg-v1`).
- Valor inicial: `data/config.js` (`window.PALMAS_CONFIG`); se vazio, vale o padrão do código (lista `P0` + blocos `mig*`).
- Regra de versão: se `PALMAS_CONFIG.rev` for maior que o `rev` guardado no navegador, o publicado substitui o local.
- Blocos `if(!CFG.migN){...}` rodam uma vez por navegador (ajustes de dados antigos). Depois que o `config.js` oficial existir, a verdade passa a ser ele.
- Favoritos do visitante: `localStorage`, chave `palmas-map-fav-v1` (não vão para o `config.js`).

## `js/app.js` por seções (procure o comentário `/* ===== ... ===== */`)
- Início: dados padrão, carregamento do `CFG`, botões, lista lateral, zoom/arrasto, cartão.
- ADMIN: senha (SHA-256 no navegador), abas Locais / Categorias / Geral, exportação.
- QUADRAS E AVENIDAS: constantes `QD` e `AVD`, busca e camada ▦.
- FASE 1: tour guiado, roteiro de favoritos, hora do dia.
- FASE 3: marcadores e "aberto agora" (horário de Palmas, `America/Araguaina`).
- MOVIMENTO SUAVE e MENU LATERAL RECOLHÍVEL.

## Cuidados
- Não renomeie ids usados pelo JS (`#stage`, `#tx`, `#tint`, `#card`, `#vp`, `#pub`, `#adm`...).
- `#tx` e as bandeiras (`#flagpipa`, `#flaghgp`) ficam em `index.html`; se refizer a camada de textos com `tools/2_extrair_textos.py`, mantenha as bandeiras.
- A senha do Admin é uma barreira simples no navegador, não segurança de servidor.
