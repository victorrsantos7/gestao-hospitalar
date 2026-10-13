# cadastro-transferencias Specification

## Purpose
Permitir registrar e consultar a movimentação do paciente entre setores durante
uma internação, preservando um histórico operacional protegido e rastreável.

## Requirements

### Requirement: Registro de transferência autorizado

O sistema MUST permitir que enfermagem/gestão ou admin registre uma transferência
para uma internação ativa, informando data, destino e motivo. A transferência
MUST permanecer vinculada à internação e não MUST alterar automaticamente o leito
físico nesta etapa.

#### Scenario: Transferência válida

- **WHEN** usuário autorizado informa internação ativa, data válida, destino e motivo
- **THEN** o sistema cria a transferência e confirma seu identificador

#### Scenario: Múltiplas transferências

- **WHEN** usuário autorizado registra nova transferência para uma internação ativa que já possui transferências
- **THEN** o sistema cria o novo registro mantendo os anteriores

#### Scenario: Internação encerrada

- **WHEN** usuário autorizado tenta transferir uma internação com alta
- **THEN** o sistema rejeita a operação e não cria transferência

#### Scenario: Papel sem permissão

- **WHEN** recepcionista ou médico tenta registrar transferência
- **THEN** o backend rejeita a operação e não grava dados

### Requirement: Consulta do histórico de transferências

O sistema MUST permitir que enfermagem/gestão ou admin consulte as transferências
de uma internação, retornando data, destino e motivo em ordem cronológica.

#### Scenario: Histórico permitido

- **WHEN** usuário autorizado consulta internação existente
- **THEN** o sistema retorna todas as transferências vinculadas em ordem de data

#### Scenario: Histórico negado

- **WHEN** recepcionista, médico ou pessoa sem sessão solicita transferências
- **THEN** o backend rejeita a operação e não retorna dados de movimentação

#### Scenario: Internação inexistente

- **WHEN** usuário autorizado solicita histórico de internação inexistente
- **THEN** o sistema rejeita a consulta sem retornar registros
