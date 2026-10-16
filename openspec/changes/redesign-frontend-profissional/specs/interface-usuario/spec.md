# interface-usuario Specification

## ADDED Requirements

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
