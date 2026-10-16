# Design

## Context

O aplicativo não define `rx.Model`, não abre sessões SQL e não consulta o
SQLite. `db_url` ativa uma infraestrutura cujo único conteúdo remanescente é a
tabela técnica `alembic_version`; preflight, testes, backup e documentação
continuam acoplados a ela. O Reflex aceita `db_url=None`, e seus pacotes de
banco são opcionais. Ver [proposal.md](./proposal.md) para a motivação.

## Goals / Non-Goals

**Goals:**

- Fazer compilação, inicialização, preflight, backup e restauração funcionarem
  sem arquivo ou configuração de banco local.
- Remover integralmente o caminho operacional SQLite/Alembic, sem deixar
  verificações ou instruções órfãs.
- Reduzir dependências diretas somente quando a árvore instalada comprovar que
  elas não são exigidas pelo Reflex ou por outro pacote.
- Alinhar instruções de arquitetura e documentação ao Xano como persistência
  exclusiva.

**Non-Goals:**

- Alterar o cliente, os contratos, os dados ou a autorização do Xano.
- Reescrever changes arquivadas ou apagar o histórico Git das migrações.
- Remover a regra genérica `*.db` do `.gitignore`.
- Criar uma alternativa local para indisponibilidade do Xano.

## Decisions

### Remoção integral em vez de apenas retirar `db_url`

Serão removidos a configuração, o arquivo local, o ambiente Alembic, os testes
de migração e todas as etapas operacionais que os consomem. Retirar somente
`db_url` deixaria o preflight bloqueado, o backup copiando artefatos obsoletos e
uma arquitetura contraditória.

Alternativa descartada: conservar Alembic como histórico executável. O Git e as
changes arquivadas já preservam esse histórico; executá-lo continua criando um
banco que a aplicação não usa.

### Preflight valida somente dependências reais

O preflight deixará de aceitar caminho de banco e de verificar head, revisão ou
schema. Continuará validando Python, pacotes, configuração Xano, porta, suíte,
compilação, conectividade e estado do working tree.

Alternativa descartada: tornar a verificação SQLite opcional. Isso manteria
ramificações e dependências sem um fluxo funcional que as justificasse.

### Backup preserva código e Xano, não o banco vazio

O pacote continuará incluindo manifesto, hashes, commit, working tree,
dependências, configuração sem segredos e export do workspace Xano. Serão
retiradas a cópia do banco, a configuração Alembic e a validação SQLite na
restauração.

Backups externos existentes não serão alterados; o restaurador continuará
validando seus hashes, mas o novo contrato não promete validar bancos antigos.

### Dependências removidas por evidência

`alembic`, `sqlmodel` e `SQLAlchemy` são candidatos diretos. Antes de editar o
manifesto, a implementação verificará os requisitos instalados e removerá
também pins auxiliares apenas quando nenhum pacote remanescente depender deles.
Um ambiente limpo será reinstalado a partir do manifesto e validado com
`pip check`, testes e compilação.

Alternativa descartada: remover todos os nomes associados a SQL por inspeção
visual, pois algum deles pode continuar sendo dependência transitiva de outra
funcionalidade.

### História preservada, arquitetura ativa atualizada

Changes arquivadas e commits não serão modificados. Documentos normativos e
operacionais ativos serão atualizados ou removidos para não afirmar que existem
modelos locais ainda não migrados. `*.db` permanece no `.gitignore` como defesa
contra arquivos acidentais.

## Risks / Trade-offs

- **[Risco] Algum import indireto depender dos pacotes de banco** → recriar o
  ambiente e executar `pip check`, suíte completa e compilação antes de concluir.
- **[Risco] Scripts ou documentos continuarem apontando para Alembic** → fazer
  varredura final fora dos archives e aceitar referências apenas quando forem
  explicitamente históricas.
- **[Risco] Perda de fallback local em indisponibilidade do Xano** → não existe
  fallback funcional hoje; documentar claramente que a operação depende do
  serviço remoto.
- **[Trade-off] Comandos `reflex db ...` deixam de ser aplicáveis** → coerente
  com a ausência de modelos e persistência local.

## Migration Plan

1. Remover `db_url` e os artefatos Alembic/testes de migração.
2. Simplificar preflight, backup e restauração.
3. Auditar e reduzir dependências, depois recriar o ambiente Python.
4. Atualizar documentação, instruções do projeto e specs ativas.
5. Excluir o banco local ignorado sem produzir backup e confirmar que nenhum
   novo arquivo é criado por compilação ou inicialização.
6. Executar suíte completa, compilação, preflight, backup/restauração e smoke
   test HTTP em produção.

Rollback: restaurar o commit anterior recria a configuração e os artefatos
versionados. O arquivo `gestao_hospitalar.db` não contém dados funcionais e não
será preservado.
