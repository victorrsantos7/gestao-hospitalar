# Interface do Usuário Specification

## Purpose

Definir uma experiência visual consistente, responsiva e segura para a
navegação, consulta e execução das ações do sistema hospitalar.

## Requirements

### Requirement: Navegação persistente

O sistema MUST exibir em todas as páginas internas uma navegação com os módulos
permitidos ao papel do usuário, destacando o módulo atual, sem exigir retorno ao
dashboard para trocar de módulo. A navegação MUST exibir apenas módulos que o
papel pode acessar.

#### Scenario: Troca direta de módulo

- **WHEN** usuário autenticado está em qualquer página interna
- **THEN** a navegação lateral permite abrir outro módulo permitido em um clique

#### Scenario: Módulo atual destacado sem espera

- **WHEN** o usuário abre um módulo pelo menu
- **THEN** o item do módulo aparece destacado já na primeira renderização, sem aguardar as consultas ao servidor

#### Scenario: Módulo não permitido

- **WHEN** o papel do usuário não possui acesso a um módulo
- **THEN** a navegação não exibe esse módulo

#### Scenario: Tela estreita

- **WHEN** a largura da tela é pequena
- **THEN** a navegação fica disponível em uma gaveta acionada por botão

### Requirement: Feedback de ação

O sistema MUST sinalizar visualmente cada ação que consulta ou grava dados: o
botão acionado MUST exibir carregamento e os demais botões de ação MUST ficar
desabilitados até o fim da operação; ao terminar, o sistema MUST exibir uma
notificação de sucesso ou de erro.

#### Scenario: Ação em andamento

- **WHEN** o usuário aciona cadastro, alta, transferência, exclusão ou login
- **THEN** o botão mostra carregamento e não aceita novo clique até a resposta

#### Scenario: Sucesso

- **WHEN** a operação conclui com êxito
- **THEN** o sistema exibe uma notificação de sucesso com a mensagem do evento

#### Scenario: Erro

- **WHEN** a operação falha ou é rejeitada por validação
- **THEN** o sistema exibe notificação de erro e mantém a mensagem junto ao formulário

### Requirement: Confirmação de ações irreversíveis

O sistema MUST pedir confirmação explícita antes de registrar alta, registrar
transferência ou excluir convênio.

#### Scenario: Confirmação cancelada

- **WHEN** o usuário cancela o diálogo de confirmação
- **THEN** nenhuma operação é enviada

### Requirement: Apresentação de dados

O sistema MUST apresentar listas de cadastros em tabelas com busca, estados
vazios orientativos e badges de status com cor semântica, e MUST apresentar o
histórico do paciente em linha do tempo ordenada como recebida do servidor.

#### Scenario: Busca na lista

- **WHEN** o usuário digita um termo no campo de busca da tabela
- **THEN** a tabela exibe apenas registros que contenham o termo, sem nova consulta ao servidor

#### Scenario: Lista vazia

- **WHEN** não há registros ou nenhum corresponde à busca
- **THEN** o sistema exibe um estado vazio com ícone e orientação

### Requirement: Indicadores no dashboard

O dashboard MUST exibir indicadores de leitura somente para os recursos que o
papel pode consultar, sem expor dados sensíveis de pacientes.

#### Scenario: Sem dados de pacientes no navegador

- **WHEN** o painel é carregado
- **THEN** apenas totais são mantidos no estado, e não listas de pacientes, médicos ou atendimentos

#### Scenario: Leitura recente reaproveitada

- **WHEN** o usuário volta ao painel em menos de 60 segundos
- **THEN** os indicadores anteriores são exibidos sem nova consulta ao servidor

#### Scenario: Papel com acesso parcial

- **WHEN** um papel não pode consultar um recurso
- **THEN** o indicador correspondente não é exibido e o recurso não é consultado

### Requirement: Indicação de carregamento

O sistema MUST indicar visualmente que uma leitura está em andamento, exibindo
esqueleto no lugar de listas e indicadores ainda sem dados, mantendo visível a
leitura anterior com aviso de atualização, e MUST bloquear os botões de ação até
o término.

#### Scenario: Primeira leitura

- **WHEN** a página abre e a leitura ainda não chegou
- **THEN** a lista mostra esqueleto de carregamento e não a mensagem de lista vazia

#### Scenario: Retorno a uma tela já lida

- **WHEN** o usuário volta a uma tela cuja leitura anterior ainda está no estado
- **THEN** os dados anteriores permanecem visíveis com o aviso "Atualizando" até a nova leitura chegar

### Requirement: Atualizar e limpar a tela

O sistema MUST oferecer, nas telas de consulta, a ação Atualizar, que recarrega
os dados do servidor e confirma o resultado, e a ação Limpar, que remove da tela
a leitura, o detalhe aberto, a busca, o formulário e as mensagens, sem excluir
dados no servidor.

#### Scenario: Atualizar

- **WHEN** o usuário aciona Atualizar
- **THEN** o botão mostra carregamento, a lista é recarregada e uma notificação confirma a atualização ou informa o erro

#### Scenario: Limpar

- **WHEN** o usuário aciona Limpar
- **THEN** a lista, o detalhe, a busca e os campos da tela são esvaziados e nenhum registro é alterado no servidor

### Requirement: Paginação das listas

O sistema MUST permitir navegar por todas as páginas das listas de pacientes e
médicos, exibindo a faixa de registros e o total, e MUST manter os seletores do
formulário de atendimentos completos independentemente da página exibida.

#### Scenario: Navegar entre páginas

- **WHEN** a lista tem mais de uma página e o usuário aciona Próxima ou Anterior
- **THEN** a página correspondente é carregada, o botão mostra carregamento e a busca é zerada

#### Scenario: Limites

- **WHEN** o usuário está na primeira ou na última página
- **THEN** o botão que levaria além do limite fica desabilitado

#### Scenario: Busca limitada à página

- **WHEN** o usuário busca em uma lista paginada
- **THEN** a busca considera apenas a página exibida e a interface informa isso

#### Scenario: Seletores completos no atendimento

- **WHEN** existem mais pacientes ou médicos do que cabem em uma página
- **THEN** o formulário de atendimento oferece todos eles para seleção

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
