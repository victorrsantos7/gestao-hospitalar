# Sistema de Gestão Hospitalar

Aplicação full-stack em [Reflex](https://reflex.dev) para gerenciar a jornada
do paciente dentro do hospital: cadastro de pacientes, médicos e convênios,
atendimentos, diagnósticos, internações, leitos e transferências.

## Documentação do projeto

- [AGENTS.md](AGENTS.md) — instruções para agentes de IA que trabalham neste projeto.
- [docs/project-overview.md](docs/project-overview.md) — visão geral do sistema.
- [docs/domain-model.md](docs/domain-model.md) — conceitos e relacionamentos do domínio.
- [openspec/config.yaml](openspec/config.yaml) — contexto e regras dos workflows do OpenSpec.
- [openspec/specs/](openspec/specs) — comportamento consolidado do sistema.
- [openspec/changes/](openspec/changes) — mudanças em andamento e histórico.

## Ambiente de desenvolvimento

Pré-requisitos: Python 3.10+.

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
reflex run
```

A aplicação fica disponível em `http://localhost:3000` (backend em `:8000`).

## Desenvolvimento

Mudanças são conduzidas via OpenSpec, seguindo o ciclo Explore → Propose →
Review → Apply → Archive. Veja `AGENTS.md` para as regras completas.
