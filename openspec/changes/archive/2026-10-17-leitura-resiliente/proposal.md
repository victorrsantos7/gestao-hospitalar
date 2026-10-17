# Proposal

## Why

Algumas telas mostravam "Não foi possível carregar..." ao abrir e o erro
continuava mesmo depois de sair e voltar. O log (`xano_request_end`) mostrou a
causa principal: rajadas de HTTP 429 (limite de requisições do Xano) em
`/patients`, `/atendimentos`, `/leitos`, `/internacoes` e outras, geradas pelo
painel (cinco contagens em paralelo mais até 20 páginas de atendimentos) e
tratadas como erro genérico, sem nova tentativa. Além disso:

- latência de leitura de até ~5,7 s com timeout de 10 s;
- uma conexão HTTP (e um TLS) nova a cada requisição;
- token de sessão recusado (401) caía na mesma mensagem genérica, sem levar o
  usuário ao login;
- sem como repetir a leitura sem recarregar a página.

## What Changes

- Cliente Xano: leituras (GET) repetidas até 3 vezes com espera crescente
  (0,5 s, 1 s, 2 s; teto de 5 s) em 429, 502, 503, 504 e erro de conexão;
  `Retry-After` respeitado. Timeout repete no máximo uma vez. Escritas nunca
  são repetidas.
- Conexão HTTP reaproveitada entre requisições, timeout de conexão separado do
  de leitura e no máximo 3 requisições simultâneas ao Xano.
- Limite local por janela (padrão 8 requisições a cada 20 s, `XANO_LIMITE_REQUISICOES` e
  `XANO_JANELA_SEGUNDOS`) e pausa coordenada ao receber 429: o 429 do Xano vem de uma
  janela de tempo, e retries curtos de várias threads a mantinham esgotada (o painel
  falhava por mais de um minuto). Espera do 429: `Retry-After` (até 30 s) ou 2 s, 4 s, 8 s.
- 429 e 5xx passam a ser "Xano indisponível"; 401 com token de sessão vira
  `XanoSessionExpiredError`.
- `XANO_MAX_TENTATIVAS` (1 a 5, padrão 3).
- Sessão expirada: aviso e retorno ao login, após a leitura da página e dos
  gráficos.
- Falha de leitura: aviso com botão "Tentar novamente", que repete a leitura da
  tela atual. Os últimos dados lidos continuam na tela.

Fora do escopo: cache de leituras entre sessões, renovação automática de token
e mudanças no Xano.

## Capabilities

### Modified Capabilities

- `persistencia-xano`: tratamento de falhas transitórias, limite de requisições e sessão expirada.
- `interface-usuario`: aviso de falha de leitura com nova tentativa.

## Impact

- `xano_client.py` (`_request`, `XanoConfig`, `XanoSessionExpiredError`).
- `auth_state.py` (`_registrar_falha`, `verificar_sessao`, `tentar_novamente`,
  `leitura_falhou`; 22 blocos `except XanoError` registram a falha).
- `ui/componentes.py` (`mensagem_erro`) e `gestao_hospitalar.py` (`ao_carregar`).
- Testes: `test_xano_client.py` e `test_auth_state_feedback.py`.
