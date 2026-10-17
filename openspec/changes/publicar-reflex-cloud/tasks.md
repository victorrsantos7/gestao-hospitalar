# Tasks

## 1. Configuração

- [x] 1.1 `configuracao.py` e `rxconfig.py` com `GESTAO_CORS_ORIGINS`; verificar com testes e importando o `rxconfig`.
- [x] 1.2 Log em saída padrão e plano B para pasta sem escrita; verificar com testes.
- [x] 1.3 `cloud.yml`, `.env.cloud.example` e `.gitignore`; verificar com testes de proteção de segredos.

## 2. Documentação

- [x] 2.1 Guia `docs/publicacao-reflex-cloud.md` e nota no README.

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 3.2 Primeiro deploy (login, painel, ajuda, gráficos, CORS efetivo confirmados pelo usuário em https://gestao-hospitalar-neon-apple.reflex.run) e guia ajustado com o que o ambiente real mostrou.
- [ ] 3.3 `revisao-tecnica` e pacote de entrega.
