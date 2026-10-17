# persistencia-xano Specification

## ADDED Requirements

### Requirement: Leituras resilientes a falhas transitórias

O sistema MUST repetir leituras (GET) ao Xano que falharem por limite de
requisições (429), indisponibilidade temporária (502, 503, 504) ou erro de
conexão, com espera crescente e no máximo o número configurado de tentativas
(padrão 3), respeitando o `Retry-After` quando informado. Escritas MUST NOT ser
repetidas automaticamente.

#### Scenario: Limite de requisições superado e recuperado

- **WHEN** uma leitura recebe 429 e a nova tentativa recebe 200
- **THEN** a leitura conclui com os dados da resposta de sucesso, sem erro para o usuário

#### Scenario: Falha persistente

- **WHEN** todas as tentativas de uma leitura recebem 429 ou 503
- **THEN** o fluxo informa que o serviço está temporariamente indisponível

#### Scenario: Escrita sem resposta

- **WHEN** uma escrita (POST, PATCH ou DELETE) recebe 503 ou excede o timeout
- **THEN** a requisição não é repetida e o fluxo informa a indisponibilidade

### Requirement: Uso controlado da conexão com o Xano

O sistema MUST reaproveitar a conexão HTTP com o Xano entre requisições e MUST
limitar as requisições simultâneas para evitar rajadas que excedam o limite do
serviço.

#### Scenario: Leituras em paralelo

- **WHEN** o painel lê vários recursos ao mesmo tempo
- **THEN** no máximo três requisições ao Xano ficam em andamento simultaneamente

#### Scenario: Limite por janela

- **WHEN** o número de requisições na janela configurada atinge o limite local
- **THEN** a próxima requisição espera a vez em vez de ser enviada e receber 429

#### Scenario: Pausa depois de 429

- **WHEN** o Xano responde 429 a uma requisição
- **THEN** as demais requisições também esperam o tempo indicado (`Retry-After`, até 30 s) antes de insistir

### Requirement: Sessão expirada distinta de indisponibilidade

O sistema MUST distinguir o token de sessão recusado pelo Xano (401) de falhas
de disponibilidade, e MUST NOT tratar a recusa de credenciais do login como
sessão expirada.

#### Scenario: Token recusado em uma leitura

- **WHEN** uma leitura com o token da sessão recebe 401
- **THEN** o erro é de sessão expirada, não de indisponibilidade

#### Scenario: Login recusado

- **WHEN** o login recebe 401 ou 403
- **THEN** o erro é de credenciais inválidas
