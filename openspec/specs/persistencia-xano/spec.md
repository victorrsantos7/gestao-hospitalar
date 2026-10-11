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

O sistema MUST enviar e receber dados dos fluxos migrados por requisicoes
autenticadas ao Xano e MUST validar o formato das respostas antes de usa-las.

#### Scenario: Consulta remota bem-sucedida
- **WHEN** um fluxo migrado solicita dados e o Xano responde com sucesso
- **THEN** o sistema converte a resposta para o formato esperado pelo fluxo
  sem acessar a persistencia local como fallback silencioso

#### Scenario: Resposta remota invalida
- **WHEN** o Xano responde com dados ausentes ou em formato incompativel
- **THEN** o sistema rejeita a resposta, registra um erro tecnico sem dados
  sensiveis e informa a indisponibilidade do fluxo

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
