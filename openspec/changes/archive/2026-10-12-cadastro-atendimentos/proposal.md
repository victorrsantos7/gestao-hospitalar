# Proposal

## Why

O sistema ja mantem pacientes, medicos e convenios, mas ainda nao registra o
evento que relaciona essas entidades na jornada do paciente. Esta change cria
o primeiro registro operacional do atendimento, necessario para sustentar
diagnosticos e internacoes nas proximas etapas.

## What Changes

- Criar a capacidade de registrar atendimentos vinculando paciente, medico e,
  opcionalmente, convenio.
- Armazenar data, motivo e tipo do atendimento (`consulta`, `emergencia` ou
  `retorno`) com validacao no backend.
- Permitir a consulta protegida dos atendimentos por usuarios autorizados,
  sem expor dados de autenticacao ou campos internos.
- Publicar endpoints privados no Xano e integra-los ao cliente HTTP e ao
  `AuthState` do Reflex.
- Disponibilizar uma tela `/atendimentos` com formulario e listagem conforme o
  papel autenticado.
- Manter diagnosticos, internacoes, leitos, transferencias e historico fora
  do escopo desta change.

## Capabilities

### New Capabilities

- `cadastro-atendimentos`: registro, consulta, validacao e autorizacao de
  atendimentos vinculados as entidades ja cadastradas.

### Modified Capabilities

Nenhuma.

## Impact

Serão afetados o cliente Xano, o estado de autenticacao, a matriz de
autorizacao, a nova tela Reflex e os testes automatizados. O Xano recebera uma
tabela de atendimentos e endpoints privados com validacao de referencias para
paciente, medico e convenio. Nao havera alteracao no contrato dos cadastros ja
concluidos.