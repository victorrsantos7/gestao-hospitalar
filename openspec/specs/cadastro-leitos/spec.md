# cadastro-leitos Specification

## Purpose
Permitir que a equipe de enfermagem/gestão controle o conjunto de leitos do
hospital e consulte sua disponibilidade sem editar manualmente uma ocupação.

## Requirements

### Requirement: Cadastro de leito autorizado

O sistema MUST permitir que enfermagem/gestão ou admin cadastre um leito
informando um número identificador. O número MUST ser único e o leito novo MUST
iniciar com status `livre`.

#### Scenario: Leito válido

- **WHEN** enfermagem/gestão ou admin informa um número ainda não cadastrado
- **THEN** o sistema cria o leito com status `livre` e confirma o identificador

#### Scenario: Número duplicado

- **WHEN** um usuário autorizado informa número já cadastrado
- **THEN** o sistema rejeita o cadastro e não cria um segundo leito

#### Scenario: Papel sem permissão cadastra leito

- **WHEN** recepcionista ou médico tenta cadastrar um leito
- **THEN** o backend rejeita a operação e não grava dados

### Requirement: Consulta de disponibilidade de leitos

O sistema MUST permitir que enfermagem/gestão ou admin consulte leitos com seus
números e status atuais. O status MUST refletir a ocupação ativa e não MUST ser
alterado manualmente por usuários.

#### Scenario: Consulta de leitos

- **WHEN** usuário autorizado solicita a listagem de leitos
- **THEN** o sistema retorna os leitos identificando número e status `livre` ou `ocupado`

#### Scenario: Consulta negada

- **WHEN** recepcionista, médico ou pessoa sem sessão solicita leitos
- **THEN** o backend rejeita a operação e não retorna dados de ocupação
