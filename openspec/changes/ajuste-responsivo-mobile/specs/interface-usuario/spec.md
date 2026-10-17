# interface-usuario Specification

## MODIFIED Requirements

### Requirement: Adaptação à largura da tela

O sistema MUST adaptar menu, formulários e listas à largura disponível, sem
exigir rolagem horizontal nas tabelas de cadastro e sem desperdiçar a área útil
em monitores pequenos ou grandes. Em telas de celular (até 480 px) o painel de
login e os cabeçalhos de cartão MUST exibir o conteúdo sem cortar texto nem
espremer o título.

#### Scenario: Tela de laptop

- **WHEN** a largura da tela é de 901 a 1279 px
- **THEN** o menu lateral é exibido como trilho de ícones, com o nome de cada módulo disponível como dica

#### Scenario: Largura insuficiente para formulário e lista lado a lado

- **WHEN** a largura útil não comporta o formulário e a lista na mesma linha
- **THEN** o formulário é exibido acima da lista, com os campos em colunas, e a tabela ocupa a largura inteira

#### Scenario: Monitor grande

- **WHEN** a largura da tela é de 1920 px ou mais
- **THEN** o conteúdo usa uma largura máxima maior que a de telas médias, e a partir de 2400 px a interface é ampliada em 10%

#### Scenario: Tela de login em celular

- **WHEN** a largura da tela é de até 480 px
- **THEN** o texto do painel de login (logo, título e frase) é exibido em fluxo normal, sem cortar o topo, e os destaques secundários ficam ocultos para caber sem rolagem até o botão de entrar

#### Scenario: Cabeçalho de cartão em tela estreita

- **WHEN** um cabeçalho de cartão tem título e uma ação larga (ex.: seletor de período) que não cabem lado a lado
- **THEN** a ação desce para a linha de baixo, em vez de espremer o título
