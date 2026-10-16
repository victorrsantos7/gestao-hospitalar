# Tasks

## 1. Desacoplamento do runtime

- [x] 1.1 Remover `db_url` da configuração Reflex e adicionar teste de prontidão que confirme `config.db_url is None`.
- [x] 1.2 Remover `alembic.ini`, o diretório `alembic/` e `tests/test_migrations.py`, verificando que nenhum artefato SQLite/Alembic ativo permanece rastreado.
- [x] 1.3 Excluir `gestao_hospitalar.db` local sem backup e verificar que `reflex compile --dry` não recria o arquivo.

## 2. Operação sem banco local

- [x] 2.1 Remover do preflight o parâmetro e as verificações de banco/migração, mantendo os demais gates, e verificar execução aprovada sem `gestao_hospitalar.db`.
- [x] 2.2 Retirar banco e artefatos Alembic do backup, preservando commit, working tree, configuração segura, hashes e export Xano; verificar o conteúdo de um pacote temporário.
- [x] 2.3 Retirar a validação SQLite da restauração e verificar em diretório temporário que todos os hashes continuam sendo validados e adulterações continuam rejeitadas.

## 3. Dependências e documentação

- [x] 3.1 Auditar a árvore de dependências, remover de `requirements.txt` somente os pins de banco sem consumidores remanescentes e verificar uma instalação limpa com `pip check`.
- [x] 3.2 Atualizar `AGENTS.md`, `openspec/config.yaml`, visão geral, runbook e documentação relacionada para declarar o Xano como persistência exclusiva e remover orientações operacionais SQLite/Alembic.
- [x] 3.3 Remover `docs/migracoes-locais.md`, manter `*.db` no `.gitignore` e verificar por busca que referências restantes fora dos archives sejam apenas históricas e explicitamente identificadas.

## 4. Validação integrada

- [x] 4.1 Executar a suíte completa, `reflex compile --dry`, o preflight e os testes de segurança/prontidão em ambiente sem banco local.
- [x] 4.2 Iniciar pelo BAT em produção, verificar resposta HTTP 200 e confirmar que a execução não cria `gestao_hospitalar.db` nem exige comandos `reflex db`/Alembic.
- [x] 4.3 Executar backup e restauração ensaiada em diretórios temporários, verificar integridade e confirmar que o pacote não contém banco local, configuração Alembic ou segredos.
