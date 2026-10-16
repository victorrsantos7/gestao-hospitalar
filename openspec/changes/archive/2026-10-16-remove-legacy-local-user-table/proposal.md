# Proposal

## Why

A tabela SQLite local `usuario` é um resíduo da autenticação anterior e não é
consultada pelo aplicativo, que autentica exclusivamente pelo Xano. Mantê-la
provoca um aviso de divergência de schema em toda inicialização e preserva dados
de autenticação locais sem finalidade.

## What Changes

- **BREAKING** Remover definitivamente a tabela local `usuario` e seu índice
  `ix_usuario_login`, sem backup dos registros existentes, conforme decisão
  explícita do responsável pelo ambiente.
- Criar uma nova revisão Alembic destrutiva e auditável, preservando a revisão
  histórica que originalmente criou a tabela.
- Atualizar o preflight para exigir a nova revisão e confirmar a ausência da
  tabela legada.
- Atualizar os testes de migração para validar tanto um banco criado do zero
  quanto a atualização de um banco na revisão anterior.
- Atualizar a documentação operacional para declarar que autenticação e dados
  hospitalares permanecem no Xano e que o SQLite não possui mais usuários.

Fora do escopo: remover o SQLite ou o Alembic do projeto, alterar autenticação,
usuários do Xano, papéis, permissões ou contratos da API.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `operacao-local-producao`: a migração local consistente passa a exigir a
  remoção versionada e irreversível da tabela legada `usuario`, sem backup, e a
  verificação prévia deve confirmar que ela não existe.

## Impact

- Nova revisão em `alembic/versions/`, dependente de `d21af3eecf55`.
- Banco local `gestao_hospitalar.db` atualizado para a nova revisão.
- Ajustes em `tests/test_migrations.py`, `scripts/preflight.ps1` e
  `docs/migracoes-locais.md`.
- Nenhuma mudança nos endpoints Xano ou nos fluxos atuais do aplicativo.
