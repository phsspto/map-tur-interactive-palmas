# 🗺️ Mapa Turístico Interativo de Palmas-TO

Mapa turístico ilustrado e clicável de Palmas (Tocantins): botões nos locais, quadras e avenidas pesquisáveis, tour guiado,
roteiro de favoritos (com envio por WhatsApp), filtros "o que fazer agora" / "aberto agora", visual por hora do dia e painel **Admin**
para editar tudo sem mexer em código.

É um site **estático** (HTML + CSS + JavaScript, sem servidor e sem instalação). Funciona direto no **GitHub Pages**.

## Estrutura

```
index.html          página (estrutura + camada de letras nítidas do mapa: <svg id="tx"> + bandeiras em SVG)
css/style.css       estilos
js/app.js           toda a lógica (seções marcadas com /* ===== NOME ===== */)
data/config.js      DADOS PUBLICADOS (locais, categorias, cores, marcadores, horários...) — gerado pelo Admin
assets/mapa-fundo.jpg   imagem de fundo do mapa (sem textos), 4800 px
tools/              scripts opcionais para refazer o fundo/textos a partir do PDF original
docs/COMO_FOI_FEITO.md  explicação técnica (para quem for mexer no código)
CHANGELOG.md        histórico de versões
```

## 1) Publicar no GitHub (primeira vez)

1. Entre em <https://github.com/new>, crie um repositório (ex.: `mapa-turistico-palmas`), **Public**.
2. Descompacte o `.zip`. Na página do repositório: **Add file → Upload files** e arraste **o conteúdo da pasta**
   (`index.html`, `css`, `js`, `data`, `assets`, `tools`, `docs`, `README.md`...). Clique em **Commit changes**.
   *(Se preferir pelo terminal: `git init`, `git add .`, `git commit -m "Primeira versão"`, `git remote add origin ...`, `git push -u origin main`.)*
3. Vá em **Settings → Pages**. Em *Build and deployment*, escolha **Deploy from a branch**, branch **main**, pasta **/(root)** e salve.
4. Em 1–2 minutos o site fica em `https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/`.
5. Abra o site, entre em **⚙ Admin → Geral** e preencha **Link do site** com esse endereço (é ele que vai na mensagem do roteiro enviada por WhatsApp).

> Arquivos que começam com ponto (`.nojekyll`, `.gitignore`) são opcionais; se o seu sistema não os arrastar, tudo funciona do mesmo jeito.

## 2) Como atualizar

### A) Edições do dia a dia (textos, posições, ícones, cores, marcadores, horários, novos locais)
1. No site, abra **⚙ Admin**, faça as alterações e vá em **Geral → ⬇ Baixar dados para publicar (config.js)**.
2. No GitHub, abra a pasta `data`, clique em `config.js` → ✏️ (editar) ou **Add file → Upload files** e **substitua** o arquivo. **Commit changes**.
3. Em cerca de 1 minuto todos os visitantes veem a mudança (se não aparecer, **Ctrl + F5**; o GitHub guarda cache por alguns minutos).

Detalhes úteis:
- O Admin salva no navegador de quem edita; **só vale para todos depois de publicar o `config.js`**.
- Cada `config.js` carrega um carimbo de versão: quando você publica um novo, o navegador do visitante (e o seu) passa a usá-lo automaticamente.
- A senha do Admin (guardada só como código criptográfico/hash) também vai no `config.js`, então vale em qualquer computador. Ela protege o painel, mas é verificada no navegador (não é segurança de servidor).

### B) Atualizações maiores com o Claude (novas funções, mudanças de visual etc.)
1. No repositório: **Code → Download ZIP** (ou apenas os arquivos `index.html`, `css/style.css`, `js/app.js` e `data/config.js`).
2. Envie ao Claude e descreva o que quer. Ele devolve os arquivos alterados.
3. Suba os arquivos novos no GitHub **sobrescrevendo** os antigos e dê **Commit changes**.

Dica: antes de pedir, baixe o `config.js` atualizado do Admin e envie junto, para as suas edições não se perderem.

### C) Se o PDF do mapa mudar
Os scripts de `tools/` refazem o fundo, a camada de textos e a lista de quadras/avenidas. Veja `tools/README.md`.

## 3) Levar as edições que estão no endereço antigo (versão do Claude)

As edições feitas no Admin ficam salvas no navegador **daquele endereço**. Para levá-las ao novo site:
1. No endereço antigo: **Admin → Geral → ⬇ Exportar dados (.json)**.
2. No site novo: **Admin → Geral → ⬆ Importar dados (.json)** e depois **⬇ Baixar dados para publicar (config.js)**.
3. Substitua `data/config.js` no GitHub (passo 2A).
   *(Ou envie o `.json` ao Claude, que gera o `config.js` pronto.)*

## Observações
- **Fontes:** o título e alguns textos usam fontes do Google Fonts (Oswald, Kalam, Roboto Condensed). Sem internet, o site usa fontes parecidas do sistema.
- **Tamanho:** o fundo tem ~1,3 MB; o site inteiro tem ~1,5 MB (dentro dos limites do GitHub).
- **Teste local:** abra `index.html` dando dois cliques, ou rode `python -m http.server` na pasta e acesse `http://localhost:8000`.
- **Direitos do mapa:** o mapa ilustrado é de autoria do designer indicado no PDF original (crédito *Dimensão*). Confirme a autorização para publicar.
