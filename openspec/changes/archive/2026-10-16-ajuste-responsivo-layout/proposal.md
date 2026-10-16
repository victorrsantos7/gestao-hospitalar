# Proposal

## Why

Em outro monitor o layout ocupou espaço demais: o menu lateral fixo (272 px) e
o formulário ao lado da lista deixavam pouca largura para as tabelas em telas de
1280 a 1366 px (inclui 1920 px com escala do Windows de 125% e 150%), cortando
colunas; em monitores grandes (2560 px ou mais) o conteúdo ficava limitado a uma
coluna de 1240 px.

## What Changes

- Menu lateral adaptável: 248 px em telas largas, 224 px entre 1280 e 1535 px e
  trilho de ícones (72 px, com dica de texto) entre 901 e 1279 px; a gaveta
  móvel (até 900 px) continua igual.
- Formulários com campos em colunas conforme a largura do cartão: uma coluna ao
  lado da lista e várias colunas quando o formulário ocupa a linha inteira.
- Formulário e lista se empilham quando a largura não comporta os dois lado a
  lado, para as tabelas nunca precisarem de rolagem horizontal.
- Monitores grandes: largura máxima do conteúdo de 1560 px (a partir de 1920 px)
  e 1840 px com escala de interface de 110% (a partir de 2400 px).

Fora do escopo: regras de negócio, dados, textos e comportamento dos eventos.

## Capabilities

### Modified Capabilities

- `interface-usuario`: adaptação à largura da tela.

## Impact

- `assets/styles.css` (pontos de quebra e grade de formulário).
- `ui/layout.py` (dicas de texto no menu) e `ui/componentes.py` (grade de campos).
- Páginas de pacientes, médicos, convênios, atendimentos e internações (apenas
  composição visual).