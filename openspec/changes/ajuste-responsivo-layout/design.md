# Design

## Context

O layout usava larguras fixas: menu de 272 px, formulário de 340 px e lista com
base de 460 a 520 px. Em 1280 px o conteúdo útil tinha 1008 px e a lista, 597 px,
insuficiente para tabelas de 6 a 7 colunas (colunas cortadas pelo menu e pela
rolagem). Em 2560 px o conteúdo ficava em 1240 px centralizado.

## Decisions

### Pontos de quebra por largura de viewport (CSS)

- `>= 1536 px`: menu 248 px. `1280-1535 px`: menu 224 px. `901-1279 px`: menu em
  trilho de 72 px, escondendo textos por CSS (marca, rótulos, usuário, "Sair") e
  usando o atributo `title` como dica. `<= 900 px`: gaveta (inalterado).
- `>= 1920 px`: conteúdo até 1560 px. `>= 2400 px`: até 1840 px e `--scaling: 1.1`
  do Radix (fonte e espaçamentos 10% maiores) em vez de `zoom`, que desloca
  elementos posicionados (menus e dicas).
- As escalas de 125% e 150% do Windows entram naturalmente: a largura em pixels
  CSS é a da tela dividida pela escala.

### Empilhar em vez de rolar

Formulário e lista usam `flex-wrap`. A lista tem base maior (600 a 780 px,
conforme o número de colunas) e o formulário base de 300 px; quando os dois não
cabem na linha, o formulário passa para cima e ocupa a largura toda. O teto de
380 px do formulário só vale a partir de 1500 px, para ele poder crescer quando
está sozinho na linha.

### Campos em grade

`grade_campos(...)` usa CSS grid com `repeat(auto-fit, minmax(260px, 1fr))`: uma
coluna num cartão estreito e duas ou três num cartão largo, sem depender do
ponto de quebra. Áreas de texto ocupam a linha toda (`gh-campo-largo`).

## Risks / Trade-offs

- **[Risco]** Formulário no topo empurra a lista para baixo em telas estreitas.
  **Mitigação:** em largura total os campos ficam em 2 a 3 colunas, reduzindo a
  altura do formulário.
- **[Risco]** Menu em trilho esconde os rótulos. **Mitigação:** `title` em cada
  item e ícones já usados no menu completo.

## Validation

Medição em 1100, 1280, 1366, 1536, 1920 e 2560 px de largura nas telas de
pacientes, atendimentos, internações e painel: sem overflow horizontal, sem
rolagem horizontal nas tabelas e menu no formato esperado em cada faixa.