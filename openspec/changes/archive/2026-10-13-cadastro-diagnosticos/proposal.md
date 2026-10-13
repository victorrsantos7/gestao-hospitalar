# Proposal

## Why

Os atendimentos já podem ser registrados, mas ainda não possuem o diagnóstico
clínico associado. Isso impede que o sistema represente a evolução do paciente
e limita o uso do atendimento pelo médico.

## What Changes

- Criar o cadastro de diagnósticos vinculados a um atendimento existente.
- Permitir informar descrição e data do diagnóstico, com código CID opcional.
- Permitir que médicos e administradores registrem e consultem diagnósticos.
- Exibir os diagnósticos associados ao detalhe do atendimento.
- Validar campos obrigatórios, data e referência do atendimento no backend; aceitar CID ausente.
- Negar cadastro e consulta para recepcionistas e enfermagem/gestão.
- Manter mensagens genéricas de falha e não expor dados de autenticação ou campos internos.

Fora do escopo desta change: edição e exclusão de diagnósticos, prescrição de
medicamentos, classificação automática por CID e histórico consolidado do
paciente.

## Capabilities

### New Capabilities

- `cadastro-diagnosticos`: cadastro, consulta, validação e autorização de diagnósticos vinculados a atendimentos.

### Modified Capabilities

Nenhuma.

## Impact

- Novo recurso e endpoints protegidos no grupo de API do Xano.
- Novos métodos no cliente HTTP e no `AuthState` do Reflex.
- Nova tela ou seção integrada à consulta de detalhes de atendimentos.
- Novos validadores e testes para campos, referências e autorização.
- A matriz de autorização existente já contém o recurso `diagnosticos`; a change deve aplicar essa permissão no backend e na interface.
