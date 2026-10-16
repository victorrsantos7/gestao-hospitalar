# interface-usuario Specification

## ADDED Requirements

### Requirement: Adaptação à largura da tela

O sistema MUST adaptar menu, formulários e listas à largura disponível, sem
exigir rolagem horizontal nas tabelas de cadastro e sem desperdiçar a área útil
em monitores pequenos ou grandes.

#### Scenario: Tela de laptop

- **WHEN** a largura da tela é de 901 a 1279 px
- **THEN** o menu lateral é exibido como trilho de ícones, com o nome de cada módulo disponível como dica

#### Scenario: Largura insuficiente para formulário e lista lado a lado

- **WHEN** a largura útil não comporta o formulário e a lista na mesma linha
- **THEN** o formulário é exibido acima da lista, com os campos em colunas, e a tabela ocupa a largura inteira

#### Scenario: Monitor grande

- **WHEN** a largura da tela é de 1920 px ou mais
- **THEN** o conteúdo usa uma largura máxima maior que a de telas médias, e a partir de 2400 px a interface é ampliada em 10%