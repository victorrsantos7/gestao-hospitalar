# Design

## Context

A aplicação será apresentada no Windows, executada localmente em modo Reflex
produção e consumindo o Xano remoto. Há um script `iniciar_reflex.bat`, pins de
dependências, `.env.example`, SQLite local e uma migração Alembic inicial, mas
não existe um gate único de prontidão, backup verificável ou runbook. A revisão
de segurança também identificou preconditions ausentes em endpoints de Médicos
e Convênios e mass assignment no `PATCH` de Médicos.

O working tree contém alterações locais não relacionadas. Esta change deve
evitar módulos funcionais e fazer edições cirúrgicas somente em configuração,
scripts, testes de readiness, documentação e endpoints Xano confirmados.

## Goals / Non-Goals

**Goals:**

- Produzir um caminho repetível de “verificar → respaldar → iniciar → testar”.
- Corrigir autorização remota de alta confiança sem mudar a UX existente.
- Avaliar atualização do Reflex sem arriscar o ambiente funcional atual.
- Disponibilizar validação de integração real opt-in e não destrutiva, sem
  torná-la requisito para a apresentação local.
- Tornar o estado das migrações locais explícito.

**Non-Goals:**

- Hospedar publicamente ou configurar domínio/TLS.
- Transformar o SQLite local na fonte de verdade dos fluxos já migrados.
- Adicionar funcionalidades de negócio.
- Reformatar ou restaurar arquivos funcionais com mudanças locais.
- Guardar segredos no repositório ou no backup.

## Decisions

### 1. Isolar a avaliação de upgrade

A versão candidata do Reflex será instalada em um ambiente temporário criado a
partir do manifesto atual. Só depois de testes, compilação e smoke test ela
poderá substituir os pins do ambiente principal. Em falha, o ambiente atual
permanece intocado.

Alternativa: atualizar diretamente `.venv`. Rejeitada pelo risco de inviabilizar
a apresentação e dificultar rollback.

### 2. Usar um script de preflight somente leitura por padrão

O preflight verificará arquivos, ambiente, dependências, Alembic, Git, porta,
Xano e testes. Operações mutáveis, como migração, backup ou instalação, serão
comandos separados e explícitos.

Alternativa: fazer tudo automaticamente no inicializador. Rejeitada porque uma
falha no dia da apresentação poderia modificar banco ou dependências.

### 3. Tratar Xano como ambiente remoto independente

Smoke tests reais poderão usar usuários dedicados de teste e variáveis
`XANO_TEST_*`. Quando configurados, executarão somente login e GETs autorizados.
Testes de negação poderão usar os quatro papéis; escritas ficam fora do smoke
test padrão. A execução contra o ambiente real é opcional e não bloqueia a
prontidão da apresentação local.

Alternativa: reutilizar usuários reais e dados da demonstração. Rejeitada por
risco de vazamento e alteração acidental.

### 4. Corrigir autorização no próprio Xano

Endpoints de Convênios e Médicos receberão a mesma busca do ator e precondition
de papel já usada nos endpoints protegidos. O `PATCH` de Médicos deixará de
aplicar corpo bruto e passará a declarar campos permitidos e validações.

Alternativa: confiar na matriz Reflex. Rejeitada porque chamadas HTTP diretas
contornam a UI.

### 5. Manter Alembic apenas para o SQLite local

`alembic.ini`/`env.py` serão alinhados ao `db_url` local e o procedimento
verificará `current`, `heads` e upgrade em cópia de teste. O Xano continuará
gerenciado por workspace/schema próprios, sem migração Alembic.

### 6. Backup em pasta externa e com manifesto

O backup usará uma pasta configurável fora do repositório, copiará somente
artefatos permitidos e gerará hashes SHA-256, commit atual e versão das
dependências. `.env`, tokens e logs serão excluídos. O export Xano será obtido
com CLI sem registros por padrão.

### 7. Limpar a change abandonada por lista explícita

Serão removidos somente os oito endpoints identificados pelo nome e as adições
locais correspondentes comprovadamente não usadas. Antes/depois haverá pull e
comparação. A pasta da change abandonada será removida apenas após registrar a
decisão; nenhum arquivo funcional será restaurado por atacado.

## Risks / Trade-offs

- [Upgrade do Reflex altera APIs] → Testar em ambiente isolado e manter pins
  atuais se qualquer gate falhar.
- [Testes reais dependem de internet/Xano] → Mantê-los opt-in, com skip claro e
  sem bloquear o checklist da apresentação local.
- [Correção de autorização bloqueia fluxo legítimo] → Testar matriz positiva e
  negativa com usuários dedicados antes da apresentação.
- [Migração local não representa o Xano] → Documentar explicitamente as duas
  fontes e limitar Alembic ao SQLite.
- [Backup do Xano sem registros não recupera dados remotos] → Para apresentação,
  preservar definição e configuração; documentar que backup de registros exige
  export administrativo separado.
- [Working tree sujo] → Tocar somente arquivos listados na change, inspecionar
  diffs e nunca usar reset/checkout destrutivo.

## Migration Plan

1. Criar backup externo e registrar o estado Git antes de qualquer atualização.
2. Limpar os oito endpoints abandonados com confirmação por pull do Xano.
3. Corrigir e testar autorização de Médicos/Convênios no Xano.
4. Validar Alembic em cópia do SQLite, sem migrar o banco principal até revisão.
5. Avaliar Reflex em ambiente isolado; aplicar pins somente com gates verdes.
6. Adicionar preflight, smoke tests, scripts e runbook.
7. Executar ensaio completo de backup, inicialização e restauração.

Rollback: restaurar scripts/configuração pelo commit da change, manter os pins
anteriores do Reflex e republicar o export Xano pré-change caso algum endpoint
apresente regressão.
