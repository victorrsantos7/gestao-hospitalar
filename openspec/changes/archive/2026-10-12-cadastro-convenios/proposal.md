# Proposal

## Why

O sistema precisa manter os convênios disponíveis para uso nos futuros
atendimentos, mas ainda não oferece cadastro nem consulta dessa entidade. Esta
change cria a base administrativa protegida para que recepcionistas e
administradores mantenham dados de convênio consistentes.

## What Changes

- Criar o cadastro de convênios com nome, tipo e cobertura.
- Restringir o tipo aos valores `particular`, `plano` e `SUS`.
- Validar campos obrigatórios e impedir duplicidade de convênio por nome
  normalizado.
- Disponibilizar listagem e consulta de detalhes dos convênios.
- Disponibilizar atualização e exclusão protegidas para manter o cadastro.
- Persistir e consultar convênios pela API remota do Xano.
- Adicionar a rota `/convenios` e o acesso correspondente no dashboard,
  mantendo a linguagem visual atual das telas existentes.
- Manter fora desta change o redesenho estético compartilhado das telas de
  pacientes, médicos e dashboard.

## Capabilities

### New Capabilities

- `cadastro-convenios`: Cadastro, consulta, atualização, exclusão,
  validação e autorização de convênios.

### Modified Capabilities

- Nenhuma.

## Impact

- `gestao_hospitalar/xano_client.py`: novos contratos HTTP para convênios.
- `gestao_hospitalar/auth_state.py`: estado, validações, eventos e autorização
  do fluxo de convênios.
- `gestao_hospitalar/authorization.py`: uso da permissão de convênios já
  existente na matriz fixa.
- `gestao_hospitalar/convenios.py`: nova tela Reflex de cadastro e consulta.
- `gestao_hospitalar/dashboard.py` e `gestao_hospitalar/gestao_hospitalar.py`:
  navegação e rota protegida.
- `tests/`: testes de cliente, validação, autorização e comportamento do
  estado.
- Xano: tabela e endpoints protegidos para convênios.