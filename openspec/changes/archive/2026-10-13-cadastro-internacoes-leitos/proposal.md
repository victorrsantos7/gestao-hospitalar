# Proposal

## Why

O sistema já registra atendimentos, mas ainda não controla a ocupação física
do hospital nem o período em que um paciente permanece internado. Isso impede
a equipe de enfermagem/gestão de acompanhar leitos disponíveis e altas com
segurança.

## What Changes

- Criar o cadastro de leitos identificados por número.
- Derivar automaticamente o status do leito como `livre` ou `ocupado`.
- Criar internações vinculadas a um atendimento existente e a um leito livre.
- Disponibilizar uma seleção de atendimentos elegíveis, sem exigir digitação manual de IDs.
- Registrar data de entrada, data de saída e status `internado`/`alta`.
- Liberar o leito automaticamente quando uma internação receber alta.
- Impedir duas internações ativas no mesmo leito.
- Impedir mais de uma internação para o mesmo atendimento.
- Permitir consulta e manutenção por enfermagem/gestão e admin.
- Manter edição e exclusão fora do escopo inicial.

## Capabilities

### New Capabilities

- `cadastro-leitos`: cadastro, consulta e controle de disponibilidade dos leitos.
- `cadastro-internacoes`: criação, consulta e alta de internações vinculadas a atendimentos e leitos.

### Modified Capabilities

Nenhuma.

## Impact

- Novas tabelas e endpoints protegidos no Xano para leitos e internações.
- Novos métodos no cliente HTTP e estados/eventos Reflex.
- Nova interface para gestão de leitos e internações.
- Novas validações e testes de ocupação exclusiva, vínculos e alta.
- A matriz de autorização existente já contempla `internacoes` e `leitos` para enfermagem/gestão e admin.
- Transferências e histórico consolidado permanecem para changes futuras.
