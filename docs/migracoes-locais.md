# Migrações locais

O Alembic deste repositório gerencia **somente** o arquivo SQLite local
`gestao_hospitalar.db`. Ele não cria nem altera tabelas no Xano. O schema e os
dados remotos continuam sendo administrados pelas ferramentas do próprio Xano.

O histórico mantém a revisão `d21af3eecf55`, que criou a tabela local legada
`usuario`, e a revisão `a7c4e91b2f10`, que remove definitivamente essa tabela e
seu índice. A autenticação atual usa exclusivamente o Xano; o aplicativo não
consulta usuários no SQLite.

A atualização para `a7c4e91b2f10` descarta os registros locais de `usuario` sem
backup, por decisão explícita do responsável pelo ambiente. Um downgrade pode
recriar a estrutura vazia, mas não recupera os registros removidos.

## Verificação segura

Para inspecionar o histórico:

```powershell
.\.venv\Scripts\alembic.exe current
.\.venv\Scripts\alembic.exe heads
.\.venv\Scripts\alembic.exe history
```

Para validar uma cópia sem tocar no banco principal:

```powershell
$env:GESTAO_ALEMBIC_DB_URL = "sqlite:///C:/caminho/temporario/copia.db"
.\.venv\Scripts\alembic.exe upgrade head
Remove-Item Env:GESTAO_ALEMBIC_DB_URL
```

Use barras `/` na URL SQLite, mesmo no Windows. O teste automatizado
`tests.test_migrations` valida um banco criado do zero e a atualização de um
banco com usuário legado, confirmando a revisão atual e a ausência de
`usuario`/`ix_usuario_login`.

## Aviso do Reflex sobre mudanças de schema

Após `alembic upgrade head`, o Reflex não deve mais exibir `Detected database
schema changes`, pois o banco e o metadata local ficam sem tabelas de domínio.
Não use `reflex db makemigrations` para gerenciar dados do Xano.

Confirme o estado local com:

1. `alembic current`;
2. `alembic heads`;
3. `python -m unittest tests.test_migrations`.

O preflight também confirma dinamicamente o head Alembic e bloqueia a
inicialização se a tabela `usuario` ainda existir.
