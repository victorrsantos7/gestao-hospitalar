<!-- reflex managed begin (do not edit inside this block; add custom content outside the markers) -->
# Agents

This project uses the **Reflex agent skills** — up-to-date knowledge for building full-stack Python web apps with [Reflex](https://reflex.dev). Install them first, then use them as described below.

## Installing the Skills

Before working on this project, make sure the Reflex skills are available to you.

### Claude Code

If the skills are not already available, install them yourself by running these shell commands:

```bash
claude plugin marketplace add reflex-dev/agent-skills
claude plugin install reflex@reflex-agent-skills
```

Newly installed plugins load on the next session. After installing, tell the user to restart the session so the skills auto-load; until then, read the skill files directly from `~/.claude/plugins/` when you need them.

### Other agents (Cursor, OpenCode, Codex, Pi)

```
npx skills add reflex-dev/agent-skills
```

Or clone https://github.com/reflex-dev/agent-skills and copy the `skills/` folders into your agent's skill directory (see the repo README for paths).

### Verifying

Before writing or editing any Reflex code, confirm these three skills are available: `reflex-docs`, `setup-python-env`, and `reflex-process-management`. If they are not, STOP and run the install step above — do not proceed without them.

## Using the Skills

### Reflex documentation

For anything about Reflex APIs — components, state management, events, styling, database, routing, authentication — use the **reflex-docs** skill rather than relying on memory. It carries current, version-accurate docs.

### Initializing a new Reflex project

When starting a new Reflex project or setting up a development environment, you **must** follow the **setup-python-env** skill before doing anything else.

Do not skip any steps. Do not assume a virtual environment or Reflex is already available — always verify first by following the skill's instructions in order.

After the environment is ready and Reflex is installed, run:

```bash
reflex init
```

Then proceed with the user's request.

### Managing a Reflex process

When you need to compile, run, reload, or debug a Reflex application, follow the **reflex-process-management** skill for the correct sequence and error investigation steps.
<!-- reflex managed end -->

# AGENTS.md — Instruções para Agentes de IA

Este arquivo define como os agentes de IA devem trabalhar no projeto
**Sistema de Gestão Hospitalar**. Ele complementa os documentos de contexto
(`docs/project-overview.md` e `docs/domain-model.md`), que devem ser
consultados antes de qualquer mudança significativa.

## Documentação

- Antes de realizar alterações significativas, consultar os documentos de
  contexto do projeto:
  - `docs/project-overview.md` — visão geral do sistema.
  - `docs/domain-model.md` — conceitos e relacionamentos do domínio.
  - `openspec/config.yaml` — contexto e regras dos workflows do OpenSpec.
- Manter a documentação atualizada conforme o sistema evolui.

## Arquitetura

- Respeitar a stack definida no projeto: Reflex (Python full-stack) para
  frontend e backend, com persistência via modelos Reflex (`rx.Model`) em
  banco relacional (SQLite em desenvolvimento, com possibilidade de
  migração para MySQL).
- Reflex é a tecnologia exclusiva do projeto. Não introduzir Flask, Jinja2
  ou qualquer outra tecnologia de frontend/backend sem justificativa clara
  e aprovação do grupo.
- Organizar o código por `State` (`rx.State`) e `Components` do Reflex,
  usando os mecanismos próprios do framework para eventos, páginas e
  roteamento.
- Consultar a skill `reflex-docs` para APIs atualizadas do Reflex antes de
  escrever ou alterar código.

## Código

- Reutilizar código existente quando apropriado.
- Evitar duplicação de lógica e de consultas.
- Não modificar funcionalidades não relacionadas à mudança atual sem
  justificativa.
- Manter o código legível e comentado em português quando necessário.

## Banco de dados

- O modelo conceitual é global (ver `docs/domain-model.md`), mas a
  implementação física deve ser incremental, change por change.
- Respeitar os relacionamentos definidos no modelo de domínio.
- Não criar tabelas fora do escopo da mudança atual.

## Segurança

- Regras de autorização e validação devem ser aplicadas no backend, nunca
  apenas no frontend.
- Validar entradas do usuário (CPF, CRM, campos obrigatórios).
- Não expor dados sensíveis de pacientes sem necessidade.

## Desenvolvimento

- Todas as mudanças devem ser conduzidas utilizando OpenSpec.
- Seguir o ciclo: Explore → Propose → Review → Apply → Archive.
- Implementar mudanças incrementais e verificáveis.

## Testes

- Mudanças funcionais devem possuir estratégia de verificação.
- Testar os fluxos principais (cadastro, atendimento, internação,
  transferência) antes de concluir uma change.

## Git

- Manter commits pequenos e descritivos.
- Não commitar o banco de dados local (`database.db`) nem o ambiente virtual
  (`.venv/`).
