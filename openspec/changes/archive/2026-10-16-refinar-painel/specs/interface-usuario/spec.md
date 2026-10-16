# interface-usuario Specification

## ADDED Requirements

### Requirement: Ocupação de leitos no painel

O painel MUST exibir, para papéis que consultam leitos, a taxa de ocupação como
porcentagem e barra de progresso, junto da contagem de leitos ocupados, livres e
do total.

#### Scenario: Leitos lidos

- **WHEN** há leitos cadastrados e a leitura do painel foi concluída
- **THEN** o painel mostra a taxa (ocupados dividido pelo total, arredondada), a barra e os totais

#### Scenario: Sem leitos ou sem leitura

- **WHEN** não há leitos ou a leitura falhou
- **THEN** a taxa é exibida como "—" e a barra fica vazia

### Requirement: Atendimentos por período e por tipo

O painel MUST exibir, para papéis que consultam atendimentos, o número de
atendimentos por dia (7 e 30 dias) ou por semana (12 semanas) e a distribuição
por tipo no período escolhido, sem manter no navegador a lista completa de
atendimentos.

#### Scenario: Trocar o período

- **WHEN** o usuário escolhe outro período
- **THEN** o gráfico e a distribuição por tipo são recalculados sem nova consulta ao servidor

#### Scenario: Leitura parcial

- **WHEN** o servidor devolve menos atendimentos do que o total
- **THEN** o painel informa quantos atendimentos o gráfico considera

### Requirement: Atividade recente e alertas

O painel MUST listar os eventos mais recentes entre atendimentos, internações e
altas e MUST exibir alertas para ocupação elevada (75%) ou crítica (90%), sem
leitos livres, poucos leitos livres (2 ou menos) e emergências do dia.

#### Scenario: Ocupação crítica

- **WHEN** a ocupação é de 90% ou mais e há leitos livres
- **THEN** o painel exibe um alerta de ocupação crítica

#### Scenario: Sem leitos livres

- **WHEN** não há leitos livres
- **THEN** o painel exibe um único alerta de ausência de leitos livres

#### Scenario: Papel sem acesso

- **WHEN** o papel não consulta atendimentos, leitos ou internações
- **THEN** os blocos correspondentes não são exibidos

### Requirement: Carregamento do painel em duas etapas

O painel MUST exibir indicadores, ocupação e alertas assim que as contagens
chegarem e MUST carregar gráfico, tipos e atividade em segundo plano, sem
bloquear a navegação.

#### Scenario: Leitura lenta de atendimentos

- **WHEN** a leitura dos atendimentos demora
- **THEN** os indicadores aparecem primeiro, o gráfico mostra esqueleto e o usuário pode abrir outra página imediatamente