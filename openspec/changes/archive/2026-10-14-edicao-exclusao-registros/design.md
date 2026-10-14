# Design

## Context

Convênios já implementa o ciclo completo criar/consultar/editar/excluir, com
padrão estável nos três componentes: `xano_client.py` (métodos
`atualizar_<x>`/`excluir_<x>` que chamam `PATCH`/`DELETE` em `/convenios/{id}`),
`auth_state.py` (eventos `editar_<x>`/`cancelar_edicao_<x>`/`salvar_<x>`/
`excluir_<x>` com campos de formulário reaproveitados entre criação e edição)
e `convenios.py` (UI com botões "Editar"/"Excluir" por linha e formulário que
alterna entre modo de criação e edição). Este design estende exatamente esse
padrão para Pacientes, Médicos e Atendimentos.

No backend Xano, `doctors` já expõe `PATCH /doctors/{doctors_id}` e
`DELETE /doctors/{doctors_id}` (não usados pelo frontend ainda). `patients` e
`atendimentos` só expõem `GET`/`POST` hoje — será necessário criar os
endpoints `PATCH`/`DELETE` correspondentes. Ver proposal.md para a motivação.

## Goals / Non-Goals

**Goals:**
- Mesma UX de edição/exclusão em Pacientes, Médicos e Atendimentos que já
  existe em Convênios (formulário inline reaproveitado, confirmação de
  exclusão, mensagens de sucesso/erro).
- Reaplicar nas operações de edição as mesmas validações já usadas no
  cadastro (CPF único, nome/telefone/data válidos, CRM único, tipo e
  referências válidas em atendimentos).
- Autorização consistente: editar/excluir só para papéis com o recurso
  correspondente (`recepcionista`, `admin`), igual ao cadastro.

**Non-Goals:**
- Internações continuam sem edição/exclusão genérica (ciclo de vida
  controlado por alta/transferência).
- Não alterar o endpoint `doctors_id_DELETE.xs` existente, que hoje restringe
  a exclusão a `recepcionista`/`admin` no backend — esse precondition já
  reflete a matriz de autorização e deve ser copiado para os novos endpoints
  de `patients` e `atendimentos`.
- Não introduzir exclusão em cascata: excluir um paciente ou atendimento que
  possua atendimentos, diagnósticos ou internações vinculadas é tratado como
  erro de validação (ver seção de Riscos), não como remoção em cascata.

## Decisions

- **Reutilizar o padrão de convênios em vez de criar um mecanismo genérico de
  CRUD.** Alternativa considerada: construir um componente/estado genérico de
  "editar/excluir" reutilizável pelos três módulos. Rejeitada por enquanto:
  os campos e validações de cada entidade são suficientemente diferentes
  (CPF vs. CRM vs. referências de atendimento) para que a abstração genérica
  adicione complexidade sem reduzir duplicação real; o código de Convênios já
  decidiu por essa duplicação controlada antes, mantendo consistência.
- **Adicionar precondition de papel no backend, espelhando
  `doctors_id_DELETE.xs`.** Os novos endpoints `PATCH`/`DELETE` de `patients`
  e `atendimentos` MUST verificar `$auth` e o papel do ator
  (`recepcionista`/`admin`) antes de aplicar a alteração, assim como já
  acontece em `doctors`. Isso garante defesa em profundidade mesmo que o
  frontend seja contornado.
- **Exclusão com verificação de vínculos.** Antes de excluir paciente,
  médico ou atendimento, o endpoint `DELETE` MUST verificar se existem
  registros dependentes (atendimentos, diagnósticos, internações ou
  transferências que referenciam o registro) e retornar erro de validação
  nesse caso, evitando órfãos no banco. Alternativa considerada: permitir a
  exclusão e deixar referências quebradas — rejeitada por violar a
  integridade do modelo descrito em `docs/domain-model.md`.
- **Edição reaproveita os mesmos campos de formulário do cadastro.** Ao
  clicar em "Editar", o formulário de criação é preenchido com os dados do
  registro selecionado (como já ocorre em `editar_convenio`), evitando criar
  um segundo conjunto de campos de estado.

## Risks / Trade-offs

- [Exclusão de paciente/médico/atendimento com vínculos impede a operação] →
  Mitigação: mensagem de erro clara orientando o usuário (ex.: "Não é
  possível excluir: paciente possui atendimentos registrados"), igual ao
  tratamento de erro já usado em outras operações.
- [Endpoints novos no Xano exigem deploy/push manual via CLI, fora do
  controle de versão do Reflex] → Mitigação: seguir o mesmo processo já
  usado para corrigir `atendimentos_GET.xs` (pull, editar `.xs`, validar,
  push) e documentar nos tasks.
- [Divergência de autorização entre frontend (`auth_state.py`) e backend
  (precondition em XanoScript)] → Mitigação: os dois lados devem checar
  exatamente os papéis `recepcionista`/`admin`, replicando o padrão já
  existente em `doctors_id_DELETE.xs`.

## Migration Plan

1. Criar os endpoints Xano `patients/{patients_id}` (`PATCH`, `DELETE`) e
   `atendimentos/{atendimentos_id}` (`PATCH`, `DELETE`) via Xano CLI (pull,
   criar `.xs`, validar, push).
2. Adicionar os métodos correspondentes em `xano_client.py`.
3. Adicionar eventos e estados de edição em `auth_state.py` para os três
   módulos.
4. Adicionar botões/formulários de edição e exclusão em `pacientes.py`,
   `medicos.py` e `atendimentos.py`.
5. Cobrir com testes unitários (`tests/test_auth_state_*.py`).
6. Validar manualmente em cada papel (recepcionista, admin, médico,
   enfermagem/gestão) antes do archive.

Rollback: reverter o commit da change; os endpoints novos no Xano podem
permanecer sem uso caso o rollback seja só no frontend (não introduzem
breaking changes nos endpoints existentes).
