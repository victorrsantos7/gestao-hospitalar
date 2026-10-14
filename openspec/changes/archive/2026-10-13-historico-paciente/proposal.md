# Proposal

## Why

O sistema já registra atendimentos, diagnósticos, internações e transferências,
mas essas informações ainda estão separadas por módulo. A equipe autorizada
precisa consultar a jornada completa do paciente em uma linha do tempo única,
sem reunir manualmente dados de várias telas.

## What Changes

- Criar uma consulta consolidada da jornada do paciente.
- Reunir atendimentos, diagnósticos, internações e transferências em uma linha do tempo.
- Ordenar os eventos cronologicamente, identificando tipo, data e dados operacionais.
- Permitir seleção de paciente sem digitação manual de IDs.
- Restringir consulta a enfermagem/gestão e admin conforme a matriz de autorização.
- Exibir mensagens genéricas em falhas parciais ou remotas.
- Manter alterações de pacientes, atendimentos e demais registros fora do escopo.

## Capabilities

### New Capabilities

- `historico-paciente`: consulta consolidada e protegida da jornada do paciente.

### Modified Capabilities

Nenhuma.

## Impact

- Novo endpoint protegido no Xano para consulta consolidada.
- Cliente HTTP, validadores e estado Reflex para seleção e linha do tempo.
- Nova rota/tela de histórico acessível pelo dashboard para enfermagem/gestão e admin.
- Novos testes de ordenação, composição de eventos, autorização e falhas.
- O histórico será somente leitura e reutilizará os registros já existentes, sem duplicar dados.
