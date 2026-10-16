# Tasks

## 1. Migração destrutiva versionada

- [x] 1.1 Criar uma revisão Alembic dependente de `d21af3eecf55` que remova `ix_usuario_login` e `usuario`, recrie somente a estrutura vazia no downgrade e verificar os comandos `alembic heads` e `alembic history`.
- [x] 1.2 Atualizar os testes de migração para cobrir banco criado do zero e atualização com registro legado, verificando em ambos a nova revisão e a ausência de `usuario` e `ix_usuario_login`.

## 2. Operação local

- [x] 2.1 Atualizar o preflight para exigir dinamicamente o head Alembic atual e confirmar a ausência da tabela legada, verificando que ele rejeita uma cópia ainda em `d21af3eecf55`.
- [x] 2.2 Atualizar `docs/migracoes-locais.md` para documentar a remoção sem backup, a autenticação exclusiva pelo Xano e a limitação do downgrade, verificando que o roteiro não orienta preservar os registros locais.

## 3. Aplicação e validação

- [x] 3.1 Aplicar `alembic upgrade head` diretamente em `gestao_hospitalar.db`, sem criar backup, e verificar por consulta SQLite a nova revisão e a inexistência de `usuario` e `ix_usuario_login`.
- [x] 3.2 Executar a suíte completa, `reflex compile --dry` e o preflight; iniciar pelo BAT e verificar resposta HTTP 200 sem o aviso `Detected database schema changes`.
