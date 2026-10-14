# Proposal

## Why

O sistema já demonstra os fluxos centrais, mas ainda depende de preparação
manual e não possui uma verificação reproduzível de que ambiente, banco local,
Xano, permissões, backup e inicialização estão prontos antes da apresentação.
Esta change reduz o risco operacional sem alterar os módulos funcionais já
concluídos.

## What Changes

- Avaliar a compatibilidade da versão mais recente estável do Reflex em
  ambiente isolado e atualizar somente se toda a suíte, a compilação e o smoke
  test passarem; caso contrário, manter `0.9.12` e registrar o bloqueio.
- Revisar a única migração Alembic existente, alinhar a configuração ao SQLite
  local do Reflex e eliminar o aviso de schema sem criar migrações vazias ou
  alterar dados do Xano.
- Disponibilizar testes de integração reais e não destrutivos contra o Xano
  para configuração, autenticação e consultas essenciais, habilitados somente
  por variáveis de ambiente específicas e opcionais para a operação local.
- Auditar a matriz de permissões no Reflex e as preconditions dos endpoints
  Xano, verificando negação por padrão, proteção de dados e ausência de
  credenciais em logs.
- Corrigir os endpoints Xano de Convênios e Médicos que hoje aceitam operações
  de papéis não autorizados; substituir o `PATCH` de Médicos baseado no corpo
  bruto por campos permitidos e validados, evitando mass assignment.
- Criar estratégia e script de backup local com manifesto, cobrindo banco
  SQLite, configuração sem segredos, estado do código e export do workspace
  Xano para uma pasta externa e ignorada pelo Git.
- Preparar a implantação local para apresentação no Windows, com verificação
  prévia, inicialização por `localhost`, logs, diagnóstico de porta e roteiro
  de recuperação.
- Remover somente os oito endpoints Xano criados pela change abandonada
  `edicao-exclusao-fluxos-hospitalares`, retirar suas adições locais não
  integradas e descartar os artefatos dessa change sem tocar nas demais
  mudanças locais ou funcionalidades commitadas.
- Fora do escopo: hospedagem pública, domínio, TLS, alta disponibilidade,
  migração completa para MySQL e inclusão de novas funcionalidades de negócio.

## Capabilities

### New Capabilities

- `operacao-local-producao`: prontidão operacional para executar, verificar,
  proteger, respaldar e recuperar a aplicação local usada na apresentação.

### Modified Capabilities

Nenhuma.

## Impact

- Dependências Python e ambiente virtual, com atualização condicional do
  Reflex.
- Configuração Reflex/Alembic e banco SQLite local.
- Testes de integração opcionais em `tests/`, sem usar credenciais no código.
- Scripts Windows de verificação, backup, inicialização e restauração.
- Documentação operacional em `docs/`.
- Workspace Xano: auditoria de endpoints e remoção limitada aos oito endpoints
  não utilizados da tentativa anterior.
- Não haverá alteração intencional nos módulos de Pacientes, Médicos,
  Convênios, Atendimentos, Diagnósticos, Internações, Leitos, Transferências,
  Histórico ou Relatórios.
