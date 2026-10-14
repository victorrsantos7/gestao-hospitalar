# Spec Delta

## Purpose

Fornecer uma visão consolidada e em tempo real da ocupação de leitos e das
internações ativas, para apoiar decisões operacionais de enfermagem e
gestão hospitalar.

## ADDED Requirements

### Requirement: Acesso ao relatório de ocupação de leitos
O sistema SHALL exibir a tela de relatórios apenas para usuários autenticados
cujo papel tenha o recurso `relatorios` liberado na matriz de autorização.
Usuários sem permissão SHALL ser redirecionados ao dashboard ao tentar
acessar a rota, da mesma forma que as demais telas protegidas do sistema.

#### Scenario: Papel autorizado acessa a tela
- **WHEN** um usuário autenticado com papel `enfermagem_gestao` ou `admin`
  acessa a rota `/relatorios`
- **THEN** o sistema carrega e exibe o relatório de ocupação de leitos e
  internações ativas

#### Scenario: Papel não autorizado tenta acessar
- **WHEN** um usuário autenticado com papel `recepcionista` ou `medico`
  acessa a rota `/relatorios`
- **THEN** o sistema redireciona para `/dashboard` e nenhum dado de
  relatório é carregado

#### Scenario: Item de navegação visível apenas para papéis autorizados
- **WHEN** o dashboard é exibido para um usuário autenticado
- **THEN** o item de navegação "Relatórios" aparece somente se o papel do
  usuário tiver o recurso `relatorios` liberado

### Requirement: Resumo de ocupação de leitos
O sistema SHALL exibir a contagem total de leitos cadastrados, quantos
estão com status `livre` e quantos estão com status `ocupado`, além da
lista dos leitos ocupados com seus números.

#### Scenario: Leitos livres e ocupados contabilizados corretamente
- **WHEN** existem leitos cadastrados com status `livre` e `ocupado`
- **THEN** o relatório exibe a contagem de livres, a contagem de ocupados
  e o total, de forma consistente com os dados retornados pelo backend

#### Scenario: Nenhum leito cadastrado
- **WHEN** não há nenhum leito cadastrado no sistema
- **THEN** o relatório exibe contagens zeradas e uma mensagem informando
  que não há leitos cadastrados

### Requirement: Lista de internações ativas com tempo internado
O sistema SHALL exibir a lista de internações com status `internado`,
mostrando para cada uma o número do leito, a data de entrada e a
quantidade de dias internado, calculada como a diferença entre a data
atual e a data de entrada.

#### Scenario: Internação ativa exibida com dias internado
- **WHEN** existe uma internação com status `internado` e data de entrada
  anterior à data atual
- **THEN** o relatório exibe o leito, a data de entrada e o número de dias
  internado calculado corretamente

#### Scenario: Internação com alta não aparece na lista de ativas
- **WHEN** existe uma internação com status `alta`
- **THEN** essa internação não é exibida na lista de internações ativas do
  relatório

#### Scenario: Nenhuma internação ativa
- **WHEN** não há nenhuma internação com status `internado`
- **THEN** o relatório exibe uma mensagem informando que não há
  internações ativas no momento
