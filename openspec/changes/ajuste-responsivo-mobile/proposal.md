# Proposal

## Why

Em celular (largura até ~480 px) a tela de login ficava ruim: o bloco de
texto do painel (logo, título, frase e 3 destaques) é ancorado pelo rodapé
(`position: absolute; bottom`) dentro de uma faixa de 220 px — texto e logo
não cabiam e o topo era cortado pelo `overflow: hidden` do painel. Em
cabeçalhos de cartão com uma ação larga ao lado do título (ex.: seletor de
período no Painel), a ação também podia espremer o título em vez de descer
para a linha de baixo.

## What Changes

- Tela de login: abaixo de 480 px o bloco de texto do painel volta ao fluxo
  normal (sem posicionamento absoluto) e os 3 destaques somem, para caber sem
  cortar nada; acima de 480 px o comportamento atual (painel com texto
  ancorado no rodapé e destaques visíveis) continua igual.
- Cabeçalho de cartão (`secao()`): o título e a ação à direita quebram para
  duas linhas em telas estreitas, em vez de espremer.

Fora do escopo: regras de negócio, dados e qualquer alteração de layout acima
de 480 px além do já existente.

## Capabilities

### Modified Capabilities

- `interface-usuario`: adaptação a telas de celular.

## Impact

- `gestao_hospitalar/login.py` (classe no bloco de destaques).
- `assets/styles.css` (faixa `@media (max-width: 480px)`).
- `gestao_hospitalar/ui/componentes.py` (`secao()` com `wrap="wrap"`).
