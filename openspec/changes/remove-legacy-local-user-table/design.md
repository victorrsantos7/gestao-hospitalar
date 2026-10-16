# Design

## Context

O SQLite configurado no Reflex possui apenas a tabela legada `usuario`, criada
pela revisão raiz `d21af3eecf55`. O aplicativo não define modelos locais ativos
nem consulta essa tabela; autenticação e dados do domínio são acessados pelo
Xano. O preflight atualmente fixa a revisão anterior e os testes exigem a
existência da tabela, enquanto o Reflex detecta a diferença entre o banco e o
metadata vazio.

## Goals / Non-Goals

**Goals:**

- Remover a tabela e os dados legados por uma revisão Alembic posterior.
- Validar bancos novos e bancos atualizados a partir da revisão anterior.
- Fazer o preflight comprovar a revisão atual e a ausência da tabela.
- Eliminar o aviso de divergência de schema sem ocultar mensagens do Reflex.

**Non-Goals:**

- Remover a configuração SQLite, Alembic ou o arquivo de banco.
- Alterar autenticação, autorização ou dados mantidos no Xano.
- Preservar ou exportar os registros da tabela `usuario`.

## Decisions

### Nova revisão destrutiva em vez de editar a revisão raiz

A revisão `d21af3eecf55` será preservada e uma nova revisão dependente dela
removerá primeiro o índice e depois a tabela. Isso mantém o histórico aplicável
a bancos já existentes e permite testar o caminho de atualização.

Editar a revisão raiz produziria o schema correto apenas em bancos novos, mas
deixaria bancos já marcados com `d21af3eecf55` sem uma transição versionada.

### Remoção sem backup ou downgrade restaurador de dados

Nenhum backup será criado antes da migração. O downgrade poderá recriar apenas
a estrutura vazia para manter a reversibilidade do schema, mas não poderá
recuperar registros descartados.

Essa decisão segue a instrução explícita do responsável e evita perpetuar
credenciais locais que não participam do aplicativo.

### Preflight valida revisão e schema

O preflight passará a comparar o banco e o cabeçalho Alembic com a nova revisão
e consultará `sqlite_master` para garantir que `usuario` não existe. A mensagem
de correção orientará aplicar a migração; não solicitará backup para essa tabela.

Validar somente a revisão seria insuficiente caso o arquivo fosse alterado
manualmente ou a migração tivesse sido marcada sem efetivamente remover a
tabela.

### Testes cobrem criação e atualização

O teste de migrações validará dois caminhos: `upgrade head` em banco vazio e
`upgrade d21af3eecf55` seguido de inserção de registro e `upgrade head`. Ambos
devem terminar sem a tabela, e o segundo comprovará a perda intencional do dado.

## Risks / Trade-offs

- **[Risco] Perda irreversível de usuários locais** → Aceita explicitamente; os
  usuários válidos estão no Xano e nenhum backup será produzido.
- **[Risco] Banco existente permanecer na revisão anterior** → O preflight
  bloqueará a inicialização até a aplicação da nova migração.
- **[Risco] Downgrade sugerir recuperação inexistente** → A documentação
  esclarecerá que eventual downgrade recria somente uma tabela vazia.

## Migration Plan

1. Criar e validar a nova revisão em bancos SQLite temporários.
2. Atualizar testes, preflight e documentação para a nova revisão.
3. Aplicar `alembic upgrade head` diretamente ao `gestao_hospitalar.db`, sem
   criar backup.
4. Confirmar nova revisão e ausência de `usuario`/`ix_usuario_login`.
5. Executar suíte de testes, compilação Reflex e inicialização pelo BAT.

Rollback de schema: executar downgrade para `d21af3eecf55` somente se
necessário, aceitando que a tabela será recriada vazia e os registros anteriores
não serão recuperados.
