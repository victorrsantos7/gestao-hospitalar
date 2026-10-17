# persistencia-xano Specification

## Purpose

Define uma persistencia remota segura e previsivel para que a aplicacao
consuma os dados do hospital pelo Xano sem expor segredos nem depender de um
banco local nos fluxos migrados.

## Requirements

### Requirement: Configuracao segura da API

O sistema MUST obter a URL da API do Xano por configuracao de ambiente ou
mecanismo equivalente fora do codigo-fonte. Quando o grupo de API exigir
autenticacao adicional, o sistema MUST obter essa credencial pela mesma
configuracao externa e MUST falhar de forma clara quando uma configuracao
obrigatoria estiver ausente.

#### Scenario: Configuracao completa
- **WHEN** a aplicacao inicia com URL configurada e, quando necessario,
  credencial valida configurada
- **THEN** os fluxos migrados podem criar requisicoes autenticadas ao Xano

#### Scenario: Configuracao obrigatoria ausente
- **WHEN** a aplicacao inicia sem a URL ou sem uma credencial exigida pelo grupo
  do Xano
- **THEN** a aplicacao informa o erro de configuracao sem usar credenciais
  fixas ou silenciosas

### Requirement: Comunicacao com a persistencia remota

O sistema MUST enviar e receber os dados de todos os fluxos funcionais por
requisições autenticadas ao Xano, MUST validar o formato das respostas antes de
usá-las e MUST NOT depender de banco de dados local ou fallback de persistência.

#### Scenario: Consulta remota bem-sucedida
- **WHEN** um fluxo funcional solicita dados e o Xano responde com sucesso
- **THEN** o sistema converte a resposta para o formato esperado pelo fluxo sem acessar persistência local

#### Scenario: Resposta remota invalida
- **WHEN** o Xano responde com dados ausentes ou em formato incompativel
- **THEN** o sistema rejeita a resposta, registra um erro tecnico sem dados
  sensiveis e informa a indisponibilidade do fluxo

#### Scenario: Execução sem banco local
- **WHEN** a aplicação é compilada ou iniciada em um ambiente sem arquivo e sem configuração de banco local
- **THEN** os fluxos funcionais permanecem disponíveis por meio do Xano

### Requirement: Tratamento de falhas do Xano

O sistema MUST tratar timeout, indisponibilidade, erro de autenticacao e
respostas HTTP de erro sem expor tokens, senhas ou dados sensiveis ao usuario.

#### Scenario: Xano indisponivel
- **WHEN** uma requisicao ao Xano excede o timeout ou nao consegue conectar
- **THEN** o fluxo informa que o servico esta temporariamente indisponivel e
  nao grava dados parcialmente

#### Scenario: Credencial rejeitada
- **WHEN** o Xano rejeita a credencial usada pela aplicacao
- **THEN** o sistema interrompe o fluxo, registra apenas o status tecnico e
  solicita correcao da configuracao sem revelar a credencial

### Requirement: Preservacao da integridade dos dados

O sistema MUST concluir uma operacao de escrita somente quando o Xano confirmar
sucesso e MUST evitar repetir automaticamente uma escrita que possa gerar
duplicidade sem uma estrategia de idempotencia definida.

#### Scenario: Escrita confirmada
- **WHEN** o Xano confirma a operacao de escrita
- **THEN** o sistema considera a operacao concluida e apresenta o resultado
  confirmado ao fluxo chamador

#### Scenario: Falha durante escrita
- **WHEN** uma escrita falha ou a confirmacao nao pode ser determinada
- **THEN** o sistema informa que o resultado e desconhecido ou nao concluido e
  nao executa uma nova escrita automatica sem idempotencia

### Requirement: Leituras resilientes a falhas transitórias

O sistema MUST repetir leituras (GET) ao Xano que falharem por limite de
requisições (429), indisponibilidade temporária (502, 503, 504) ou erro de
conexão, com espera crescente e no máximo o número configurado de tentativas
(padrão 3), respeitando o `Retry-After` quando informado. Escritas MUST NOT ser
repetidas automaticamente.

#### Scenario: Limite de requisições superado e recuperado

- **WHEN** uma leitura recebe 429 e a nova tentativa recebe 200
- **THEN** a leitura conclui com os dados da resposta de sucesso, sem erro para o usuário

#### Scenario: Falha persistente

- **WHEN** todas as tentativas de uma leitura recebem 429 ou 503
- **THEN** o fluxo informa que o serviço está temporariamente indisponível

#### Scenario: Escrita sem resposta

- **WHEN** uma escrita (POST, PATCH ou DELETE) recebe 503 ou excede o timeout
- **THEN** a requisição não é repetida e o fluxo informa a indisponibilidade

### Requirement: Uso controlado da conexão com o Xano

O sistema MUST reaproveitar a conexão HTTP com o Xano entre requisições e MUST
limitar as requisições simultâneas para evitar rajadas que excedam o limite do
serviço.

#### Scenario: Leituras em paralelo

- **WHEN** o painel lê vários recursos ao mesmo tempo
- **THEN** no máximo três requisições ao Xano ficam em andamento simultaneamente

#### Scenario: Limite por janela

- **WHEN** o número de requisições na janela configurada atinge o limite local
- **THEN** a próxima requisição espera a vez em vez de ser enviada e receber 429

#### Scenario: Pausa depois de 429

- **WHEN** o Xano responde 429 a uma requisição
- **THEN** as demais requisições também esperam o tempo indicado (`Retry-After`, até 30 s) antes de insistir

### Requirement: Sessão expirada distinta de indisponibilidade

O sistema MUST distinguir o token de sessão recusado pelo Xano (401) de falhas
de disponibilidade, e MUST NOT tratar a recusa de credenciais do login como
sessão expirada.

#### Scenario: Token recusado em uma leitura

- **WHEN** uma leitura com o token da sessão recebe 401
- **THEN** o erro é de sessão expirada, não de indisponibilidade

#### Scenario: Login recusado

- **WHEN** o login recebe 401 ou 403
- **THEN** o erro é de credenciais inválidas
