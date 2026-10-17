# Tasks

## 1. Cliente Xano

- [x] 1.1 Retry só para GET (429, 502, 503, 504, conexão; timeout uma vez), espera crescente e `Retry-After`; verificar com testes.
- [x] 1.2 Conexão compartilhada, timeout de conexão separado e limite de 3 requisições simultâneas; verificar com testes.
- [x] 1.3 `XanoSessionExpiredError` (401 com token) e 429/5xx como indisponível; `XANO_MAX_TENTATIVAS`.
- [x] 1.4 Limite por janela e pausa coordenada após 429 (`_Limitador`, `XANO_LIMITE_REQUISICOES`, `XANO_JANELA_SEGUNDOS`); verificar com testes e simulação.

## 2. Estado e interface

- [x] 2.1 `_registrar_falha`, `leitura_falhou`, `verificar_sessao` (via `encerrar_acao` e ao fim dos gráficos); 22 blocos de leitura/escrita ajustados.
- [x] 2.2 `tentar_novamente` por caminho da página e botão em `mensagem_erro`.

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 3.2 Validar no navegador com Xano falso lento e com 429/401: carga com retry, botão "Tentar novamente", sessão expirada, painel.
- [x] 3.3 `revisao-tecnica` e pacote de entrega.
