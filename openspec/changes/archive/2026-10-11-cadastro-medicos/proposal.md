# Proposal

## Why

O sistema já permite autenticar usuários e cadastrar pacientes, mas ainda não
possui o cadastro dos profissionais que realizam os atendimentos. Implementar
médicos agora cria a primeira dependência necessária para registrar atendimentos
com integridade e mantém o fluxo incremental do domínio hospitalar.

## What Changes

- Criar o cadastro de médicos com nome, CRM, especialidade e telefone.
- Garantir CRM único, validação de campos obrigatórios e normalização dos dados.
- Disponibilizar listagem e consulta de médicos para os papéis autorizados.
- Permitir criação para recepcionista e admin, rejeitando escrita para os demais papéis.
- Integrar as operações ao Xano com autenticação por token e tratamento de erros.
- Adicionar a rota `/medicos` e filtrar seus controles conforme o papel, mantendo a autorização no backend.

Fora do escopo: vínculo de médicos a usuários do sistema, agenda, prontuário,

autorização configurável e registro de atendimentos.

## Capabilities

### New Capabilities

- `cadastro-medicos`: cadastro, consulta e autorização de médicos.

### Modified Capabilities

Nenhuma. A matriz de autorização já contempla o recurso `medicos`; esta change
apenas implementa a funcionalidade respeitando a permissão existente.

## Impact

- Cliente HTTP Xano e endpoints de médicos.
- Estado e componentes Reflex para formulário, listagem e detalhe.
- Validação de CRM e reutilização da validação de telefones.
- Matriz de autorização, dashboard e testes automatizados.
- Nova tabela e APIs remotas no workspace Xano.