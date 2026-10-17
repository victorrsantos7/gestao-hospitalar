# Proposal

## Why

Os testadores ficam fora da rede corporativa e precisam abrir o sistema por uma
URL, sem instalar nada. O Reflex Cloud publica o app com um comando, com HTTPS e
WebSocket, mas o projeto estava preso ao uso local: origens CORS fixas em
`localhost`, log somente em arquivo e nenhuma proteção contra enviar o `.env`
local (que guarda credenciais de teste) para a nuvem.

## What Changes

- `GESTAO_CORS_ORIGINS` (lista ou `*`) define as origens permitidas; sem valor,
  continuam só as portas locais. Lógica em `gestao_hospitalar/configuracao.py`.
- Log: `GESTAO_LOG_FILE=-` usa a saída padrão, e uma pasta sem escrita não derruba
  mais o app (cai para a saída padrão).
- `cloud.yml` fixa `envfile: .env.cloud` (o padrão do Reflex seria `.env`);
  `.env.cloud.example` traz só valores não secretos; `.env.cloud` entra no `.gitignore`.
- Guia `docs/publicacao-reflex-cloud.md` (deploy a partir de máquina pessoal, com
  `--exclude-from-backend .env`) e nota no README.

Fora do escopo: Dockerfile, hospedagem própria, domínio próprio e autenticação extra
na frente do app (plano Pro do Reflex Cloud oferece acesso restrito).

## Capabilities

### New Capabilities

- `publicacao-nuvem`: configuração e proteção de segredos para publicar no Reflex Cloud.

### Modified Capabilities

- `operacao-local-producao`: origens CORS e destino dos logs configuráveis.

## Impact

- `rxconfig.py`, `logging_config.py`, `configuracao.py` (novo), `cloud.yml`,
  `.env.cloud.example`, `.gitignore`, README, `docs/publicacao-reflex-cloud.md`.
- Testes: `tests/test_publicacao.py`.
