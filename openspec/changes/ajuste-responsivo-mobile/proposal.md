# Proposal

## Why

Em celular (largura até ~480 px) a tela de login ficava ruim: o bloco de
texto do painel (logo, título, frase e 3 destaques) é ancorado pelo rodapé
(`position: absolute; bottom`) dentro de uma faixa de 220 px — texto e logo
não cabiam e o topo era cortado pelo `overflow: hidden` do painel. Em
cabeçalhos de cartão com uma ação larga ao lado do título (ex.: seletor de
período no Painel), a ação também podia espremer o título em vez de descer
para a linha de baixo.

Em teste num aparelho real (Galaxy S24) a primeira correção (texto em fluxo
normal, só os destaques ocultos) ainda não coube sem rolar: o viewport
efetivo do navegador é menor que o simulado em devtools (barra de endereço),
e o painel decorativo duplicava a marca já exibida de forma compacta no
próprio formulário. O favicon também usava o ícone padrão do scaffold do
Reflex, não a marca do sistema.

## What Changes

- Tela de login: abaixo de 480 px o painel ilustrado inteiro fica oculto —
  a marca já aparece compacta no topo do formulário, então mantê-lo era
  redundante e consumia espaço vertical sem sobra em aparelhos reais; acima
  de 480 px nada muda (painel com texto ancorado no rodapé e destaques
  visíveis).
- Cabeçalho de cartão (`secao()`): o título e a ação à direita quebram para
  duas linhas em telas estreitas, em vez de espremer.
- Favicon: gerado a partir da marca do sistema (SVG já usado em `marca()`),
  em 6 tamanhos (16 a 256 px), substituindo o ícone padrão do Reflex.

Fora do escopo: regras de negócio, dados e qualquer alteração de layout acima
de 480 px além do já existente.

## Capabilities

### Modified Capabilities

- `interface-usuario`: adaptação a telas de celular.

## Impact

- `gestao_hospitalar/login.py` (remove classe não usada após ocultar o painel inteiro).
- `assets/styles.css` (faixa `@media (max-width: 480px)`).
- `gestao_hospitalar/ui/componentes.py` (`secao()` com `wrap="wrap"`).
- `assets/favicon.ico` (gerado a partir da marca do sistema).
