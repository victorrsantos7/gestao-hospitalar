# Proposal

## Why

Após a migração integral dos fluxos funcionais para o Xano e a remoção da
tabela local legada `usuario`, o SQLite mantém apenas a revisão técnica do
Alembic e não armazena dados usados pela aplicação. Preservar essa
infraestrutura aumenta o preflight, o backup, as dependências e a documentação
sem oferecer persistência funcional.

## What Changes

- **BREAKING** Remover a configuração `db_url` do Reflex e deixar de criar ou
  exigir o arquivo local `gestao_hospitalar.db`.
- **BREAKING** Remover o ambiente e o histórico Alembic do projeto, incluindo
  testes e dependências exclusivos da persistência local.
- Simplificar o preflight para validar somente ambiente, dependências,
  configuração, porta, testes, compilação e conectividade com o Xano.
- Retirar SQLite e Alembic dos procedimentos de backup e restauração, mantendo
  referência do commit, dependências, configuração sem segredos, integridade do
  pacote e export do workspace Xano.
- Atualizar a arquitetura e a documentação para declarar o Xano como
  persistência exclusiva dos dados funcionais.
- Manter `*.db` ignorado pelo Git como proteção genérica e preservar, sem
  alteração, changes arquivadas e o histórico Git das antigas migrações.

Fora do escopo: alterar contratos ou endpoints do Xano, modificar regras de
negócio, autorização ou validação, remover dependências transitivas ainda
exigidas pelo Reflex, ou apagar backups externos já existentes.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `persistencia-xano`: a persistência remota deixa de ser descrita apenas para
  fluxos migrados e passa a ser a única persistência funcional da aplicação,
  sem banco local ou fallback.
- `operacao-local-producao`: o preflight, o backup e a restauração deixam de
  exigir SQLite/Alembic, e o requisito de migração local é removido.

## Impact

- Configuração Reflex em `rxconfig.py`.
- Remoção de `alembic.ini`, `alembic/`, `tests/test_migrations.py`,
  `docs/migracoes-locais.md` e do banco local ignorado.
- Ajustes em `scripts/preflight.ps1`, `scripts/backup_apresentacao.ps1`,
  `scripts/restaurar_backup.ps1` e respectivos testes/documentação.
- Revisão de `requirements.txt` para retirar somente dependências que deixarem
  de ser necessárias após a remoção do suporte local.
- Atualização de `AGENTS.md`, `openspec/config.yaml`, visão geral, runbook e
  documentação de atualização do Reflex.
- Nenhuma alteração nos dados, endpoints ou autenticação mantidos no Xano.
