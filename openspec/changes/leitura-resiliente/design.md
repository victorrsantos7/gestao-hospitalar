# Design

## Context

`XanoClient._request` abria um `httpx.Client` por chamada, fazia uma única
tentativa e transformava qualquer status de erro em `XanoError`. O painel lê
vários recursos de uma vez, o que dispara o limite de requisições do Xano (429,
cerca de 1 a 2 s por resposta nos logs).

## Decisions

### Repetir só leituras

GET é idempotente; POST/PATCH/DELETE com resposta perdida podem ter gravado,
então não se repetem (o teste `does_not_retry_unknown_write_result` continua
valendo). Status repetíveis: 429, 502, 503, 504, mais erro de conexão. Timeout
já consumiu o tempo todo da requisição: uma única repetição. Espera 0,5 s, 1 s,
2 s (teto 5 s); `Retry-After` do Xano tem prioridade, também com teto. Pior caso
de uma leitura que falha sempre: 3 tentativas com ~1,5 s de espera.

### Conexão compartilhada e concorrência limitada

Um `httpx.Client` por (endereço, timeout), no módulo, criado sob trava e
reaproveitado (a instância de `XanoClient` é nova a cada evento). Cabeçalhos de
autenticação vão em cada requisição, nunca no cliente compartilhado. Com
`transport` injetado (testes) cria-se um cliente próprio. Um semáforo de 3
requisições simultâneas reduz as rajadas que provocam 429 sem serializar o
painel. Timeout de conexão (5 s) separado do de leitura.

### Limite por janela e pausa coordenada

Medido na prática: depois de uma rajada, até requisições isoladas recebiam 429 por
mais de 10 s e o painel falhava por mais de um minuto. O 429 vem de uma janela de
tempo; esperas curtas (0,5 a 5 s) de várias threads só gastavam a cota de novo
(amplificação). `_Limitador` (módulo, compartilhado) combina: (1) janela deslizante
configurável (padrão 8 a cada 20 s) em que cada requisição reserva o instante de
envio, sem laço de espera, e (2) uma pausa aberta por quem recebe 429, que as
demais threads respeitam. Para 429 a espera é o `Retry-After` (teto 30 s) ou 2 s, 4 s,
8 s; os demais erros mantêm 0,5 s, 1 s, 2 s (teto 5 s). Simulação com Xano falso
limitado a 3 requisições por 2 s e 9 leituras em 5 threads: sem controle local, 12
respostas 429 e 2 leituras falhas; com ele, 9 de 9 leituras (mais lento, sem erro).

### Sessão expirada x indisponibilidade

Somente 401 com token de sessão vira `XanoSessionExpiredError` (subclasse de
`XanoAuthenticationError`, então o código existente continua válido). O login
com 401/403 segue "credenciais inválidas". Os carregadores registram a falha
com `_registrar_falha` (marca `leitura_falhou` ou `_sessao_expirada`) e o evento
`verificar_sessao`, disparado por `encerrar_acao` (fim comum das cadeias de
leitura, cadastro e login) e ao fim de `carregar_graficos`, mostra aviso e
executa `do_logout`. Assim cadastros com token recusado também voltam ao login.

### Tentar novamente

`mensagem_erro` mostra o botão enquanto `leitura_falhou` estiver ativo. A marca
é limpa ao iniciar qualquer ação (`iniciar_acao`) e no logout, de modo que o botão
só acompanha a falha de leitura mais recente. `tentar_novamente` escolhe o carregador pelo caminho da página. Erros de
escrita não ativam a marca (`leitura=False`). As listas não são zeradas na
falha, então os últimos dados lidos permanecem.

## Risks

- Leitura em falha total demora até ~12 s em vez de ~10 s (duas tentativas de
  timeout); aceitável pelo ganho nos casos transitórios.
- Sob limite do Xano o painel fica mais lento (espera a janela), mas deixa de falhar;
  o limite padrão é conservador e configurável para planos maiores.
