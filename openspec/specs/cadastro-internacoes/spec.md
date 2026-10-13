# cadastro-internacoes Specification

## Purpose
Permitir controlar o período de internação do paciente, vinculando atendimento,
leito e alta com regras de ocupação exclusiva e autorização operacional.

## Requirements

### Requirement: Criação de internação autorizada

O sistema MUST permitir que enfermagem/gestão ou admin crie uma internação
selecionando um atendimento elegível e um leito livre, informando a data de
entrada. A internação MUST iniciar com status `internado` e ocupar o leito.

#### Scenario: Seleção de atendimento elegível

- **WHEN** usuário autorizado abre o formulário de internação
- **THEN** o sistema apresenta opções com paciente, data, tipo e motivo, sem exigir digitação manual do ID

#### Scenario: Internação válida

- **WHEN** usuário autorizado informa atendimento existente, leito livre e data de entrada válida
- **THEN** o sistema cria a internação como `internado` e altera o leito para `ocupado`

#### Scenario: Atendimento já possui internação

- **WHEN** usuário autorizado tenta internar novamente um atendimento que já possui qualquer internação registrada
- **THEN** o sistema rejeita a operação e mantém a internação existente

#### Scenario: Leito ocupado

- **WHEN** usuário autorizado tenta criar internação em leito ocupado
- **THEN** o sistema rejeita a operação e não cria internação

#### Scenario: Referência inválida

- **WHEN** usuário autorizado informa atendimento ou leito inexistente
- **THEN** o sistema rejeita a operação sem criar vínculo parcial

#### Scenario: Papel sem permissão cria internação

- **WHEN** recepcionista ou médico tenta criar uma internação
- **THEN** o backend rejeita a operação e não altera leito ou atendimento

### Requirement: Consulta de internações autorizada

O sistema MUST permitir que enfermagem/gestão ou admin consulte internações
protegidas, incluindo paciente, atendimento, leito, entrada, saída e status.

#### Scenario: Listagem permitida

- **WHEN** usuário autorizado solicita internações
- **THEN** o sistema retorna os registros com suas referências e status atuais

#### Scenario: Listagem negada

- **WHEN** recepcionista, médico ou pessoa sem sessão solicita internações
- **THEN** o backend rejeita a operação e não retorna dados de internação

### Requirement: Alta e liberação de leito

O sistema MUST permitir que enfermagem/gestão ou admin registre a alta de uma
internação ativa informando data de saída válida. A internação MUST passar para
status `alta` e o leito associado MUST voltar a `livre`.

#### Scenario: Alta válida

- **WHEN** usuário autorizado informa data de saída igual ou posterior à entrada para internação ativa
- **THEN** o sistema registra a saída, altera o status para `alta` e libera o leito

#### Scenario: Alta inválida

- **WHEN** usuário autorizado informa data de saída anterior à entrada ou internação já encerrada
- **THEN** o sistema rejeita a alta e mantém a internação e o leito inalterados

#### Scenario: Papel sem permissão registra alta

- **WHEN** recepcionista ou médico tenta registrar alta
- **THEN** o backend rejeita a operação e não altera a internação
