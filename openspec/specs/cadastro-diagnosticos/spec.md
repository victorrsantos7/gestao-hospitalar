# cadastro-diagnosticos Specification

## Purpose
Permitir registrar e consultar diagnósticos clínicos vinculados aos atendimentos,
com validação dos dados e proteção por papel para preservar a privacidade do
paciente e a responsabilidade médica.

## Requirements

### Requirement: Registro de diagnóstico autorizado

O sistema MUST permitir que médico ou admin registre um diagnóstico vinculado a
um atendimento existente, informando descrição e data, podendo informar um
código CID opcional. O backend MUST aplicar a autorização antes da persistência.

#### Scenario: Médico registra diagnóstico válido

- **WHEN** um médico autenticado envia atendimento existente, descrição e data válidos, com ou sem código CID
- **THEN** o sistema cria o diagnóstico, retorna seu identificador e confirma o registro

#### Scenario: Admin registra diagnóstico válido

- **WHEN** um admin autenticado envia os dados válidos de um diagnóstico
- **THEN** o sistema cria o diagnóstico vinculado ao atendimento informado

#### Scenario: Papel sem permissão tenta registrar

- **WHEN** recepcionista ou enfermagem/gestão tenta registrar um diagnóstico
- **THEN** o backend rejeita a operação e não grava dados

### Requirement: Dados e referência válidos

O sistema MUST exigir atendimento, descrição e data. O código CID, quando
informado, MUST ser aceito como texto não vazio após a remoção de espaços. O
atendimento informado MUST existir e a data MUST estar no formato aceito pelo
sistema.

#### Scenario: Campo obrigatório ausente

- **WHEN** um usuário autorizado envia diagnóstico sem atendimento, descrição ou data
- **THEN** o sistema rejeita a operação e informa erro de validação sem criar registro

#### Scenario: Referência de atendimento inexistente

- **WHEN** um usuário autorizado informa atendimento inexistente ou inválido
- **THEN** o sistema rejeita o diagnóstico sem criar vínculo parcial

#### Scenario: Data ou texto inválido

- **WHEN** um usuário autorizado envia data inválida, descrição vazia ou código CID informado apenas com espaços
- **THEN** o sistema rejeita o diagnóstico e informa erro de validação

#### Scenario: Diagnóstico sem código CID

- **WHEN** um usuário autorizado envia atendimento, descrição e data válidos sem código CID
- **THEN** o sistema cria o diagnóstico mantendo o código CID vazio

### Requirement: Consulta de diagnósticos autorizada

O sistema MUST permitir que médico ou admin consulte diagnósticos vinculados a
um atendimento protegido. O sistema MUST impedir que recepcionista e
enfermagem/gestão consultem esses dados.

#### Scenario: Médico consulta diagnósticos do atendimento

- **WHEN** um médico autenticado consulta um atendimento existente
- **THEN** o sistema retorna os diagnósticos vinculados com descrição, código CID quando existir e data

#### Scenario: Admin consulta diagnósticos do atendimento

- **WHEN** um admin autenticado consulta um atendimento existente
- **THEN** o sistema retorna os diagnósticos vinculados ao atendimento

#### Scenario: Papel sem permissão tenta consultar

- **WHEN** recepcionista ou enfermagem/gestão solicita diagnósticos
- **THEN** o backend rejeita a operação e não retorna dados clínicos

#### Scenario: Falha no serviço remoto

- **WHEN** a consulta de diagnósticos não pode ser concluída no serviço remoto
- **THEN** o sistema mantém a sessão e informa uma falha genérica sem exibir dados parciais
