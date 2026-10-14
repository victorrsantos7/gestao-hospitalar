# Migrações locais

O Alembic deste repositório gerencia **somente** o arquivo SQLite local
`gestao_hospitalar.db`. Ele não cria nem altera tabelas no Xano. O schema e os
dados remotos continuam sendo administrados pelas ferramentas do próprio Xano.

Há uma revisão versionada, `d21af3eecf55`, que cria a tabela local legada
`usuario` e o índice único `ix_usuario_login`. Os fluxos atuais usam o Xano e
não consultam essa tabela, mas a revisão é mantida para que bancos locais
existentes continuem reproduzíveis.

## Verificação segura

Antes de qualquer migração, faça backup do banco. Para inspecionar o histórico:

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
`tests.test_migrations` cria um banco temporário desde zero, aplica todas as
revisões e confere tabela, índice e revisão.

## Aviso do Reflex sobre mudanças de schema

O Reflex pode exibir `Detected database schema changes` porque não há modelos
locais ativos correspondentes à tabela legada `usuario`. Isso não indica
divergência no Xano. Não execute `reflex db makemigrations` apenas para silenciar
o aviso: com o modelo local ausente, isso pode propor a remoção da tabela.

Na apresentação, trate o aviso como informativo se estes três comandos
confirmarem a revisão `d21af3eecf55`:

1. `alembic current`;
2. `alembic heads`;
3. `python -m unittest tests.test_migrations`.

Uma futura remoção definitiva do SQLite deve ocorrer em change própria, depois
de confirmar que nenhum dado local precisa ser preservado.
