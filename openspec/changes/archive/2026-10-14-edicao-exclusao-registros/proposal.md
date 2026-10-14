# Proposal

## Why

Hoje apenas a tela de Convênios permite editar e excluir registros; Pacientes,
Médicos e Atendimentos só oferecem cadastro e "Ver detalhes". Isso obriga
recepcionistas e administradores a corrigir erros de digitação ou remover
registros incorretos diretamente no backend, fora do sistema. Padronizar as
três telas com o mesmo padrão de edição/exclusão já usado em Convênios reduz
atrito operacional e elimina essa inconsistência de UX.

Internações ficam fora deste escopo: seu ciclo de vida já é controlado pelos
fluxos dedicados de alta e transferência (ver `cadastro-internacoes` e
`cadastro-transferencias`), e não deve existir edição/exclusão genérica desse
registro.

## What Changes

- Adicionar editar e excluir na tela de **Pacientes**, reaproveitando o mesmo
  padrão visual/UX de Convênios (formulário de edição inline, confirmação de
  exclusão, mensagens de sucesso/erro).
- Adicionar editar e excluir na tela de **Médicos**.
- Adicionar editar e excluir na tela de **Atendimentos**.
- Backend (Xano): criar os endpoints `PATCH`/`DELETE` para `patients` e para
  `atendimentos` (hoje só existe `GET`/`POST`), seguindo o mesmo padrão de
  autenticação e validação dos endpoints existentes. O endpoint de médicos
  (`doctors`) já possui `PATCH`/`DELETE` no backend — apenas o frontend
  precisa passar a utilizá-los.
- Restringir editar/excluir de Pacientes, Médicos e Atendimentos aos papéis
  que já têm o recurso correspondente na matriz fixa de autorização
  (`recepcionista` e `admin`), reaplicando as mesmas regras de validação do
  cadastro (CPF único, CRM único, tipos permitidos, referências existentes).
- Nenhuma mudança de escopo para Internações, Leitos, Transferências,
  Diagnósticos, Histórico ou Relatórios.

## Capabilities

### New Capabilities

(nenhuma)

### Modified Capabilities

- `cadastro-pacientes`: adicionar requisito de edição e exclusão de paciente
  autorizada, incluindo revalidação de CPF único e dados obrigatórios na
  atualização.
- `cadastro-medicos`: adicionar requisito de edição e exclusão de médico
  autorizada, incluindo revalidação de CRM único na atualização.
- `cadastro-atendimentos`: adicionar requisito de edição e exclusão de
  atendimento autorizada, incluindo revalidação de tipo e referências
  (paciente, médico, convênio) na atualização.

## Impact

- `gestao_hospitalar/auth_state.py`: novos eventos
  `editar_paciente`/`salvar_paciente`/`excluir_paciente`,
  `editar_medico`/`salvar_medico`/`excluir_medico`,
  `editar_atendimento`/`salvar_atendimento`/`excluir_atendimento` e estados de
  formulário de edição, seguindo o padrão já usado para convênios.
- `gestao_hospitalar/xano_client.py`: novos métodos
  `atualizar_paciente`/`excluir_paciente`, `atualizar_medico`/`excluir_medico`,
  `atualizar_atendimento`/`excluir_atendimento`.
- `gestao_hospitalar/pacientes.py`, `medicos.py`, `atendimentos.py`: novos
  botões e formulários de edição/exclusão na UI, reutilizando os estilos
  compartilhados de `estilos.py`.
- Backend Xano (workspace "Victor's Workspace"): novos endpoints
  `patients/{patients_id}` (`PATCH`, `DELETE`) e
  `atendimentos/{atendimentos_id}` (`PATCH`, `DELETE`); nenhuma mudança
  necessária em `doctors` (já existem).
- Testes: novos casos em `tests/test_auth_state_pacientes.py`,
  `tests/test_auth_state_medicos.py`, `tests/test_auth_state_atendimentos.py`.
