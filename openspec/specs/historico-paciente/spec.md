# historico-paciente Specification

## Purpose
Permitir consultar a jornada consolidada do paciente em uma linha do tempo única,
reunindo eventos clínicos e operacionais já registrados no sistema.

## Requirements

### Requirement: Consulta de histórico autorizada

O sistema MUST permitir que enfermagem/gestão ou admin selecione um paciente e
consulte seu histórico consolidado. O histórico MUST reunir atendimentos,
diagnósticos, internações e transferências disponíveis para o paciente.

#### Scenario: Consulta permitida

- **WHEN** usuário autorizado seleciona um paciente existente
- **THEN** o sistema retorna a linha do tempo com os eventos relacionados ao paciente

#### Scenario: Seleção sem digitação manual de ID

- **WHEN** usuário autorizado abre a tela de histórico
- **THEN** o sistema apresenta pacientes selecionáveis com nome e identificador interno oculto no valor da opção

#### Scenario: Paciente sem eventos

- **WHEN** usuário autorizado seleciona paciente sem atendimentos ou eventos relacionados
- **THEN** o sistema informa que não há histórico registrado

#### Scenario: Consulta negada

- **WHEN** recepcionista, médico ou pessoa sem sessão solicita histórico
- **THEN** o backend rejeita a operação e não retorna dados da jornada do paciente

### Requirement: Linha do tempo consolidada

O sistema MUST identificar cada evento por tipo e data, preservar seus dados
operacionais necessários e ordenar os eventos cronologicamente. O histórico MUST
ser somente leitura e não MUST criar, editar ou remover registros das entidades
originais.

#### Scenario: Eventos ordenados

- **WHEN** paciente possui eventos em datas diferentes
- **THEN** o sistema exibe atendimentos, diagnósticos, internações e transferências em ordem cronológica

#### Scenario: Falha parcial ou remota

- **WHEN** a consulta consolidada não pode ser concluída
- **THEN** o sistema informa falha genérica sem exibir dados parciais inconsistentes
