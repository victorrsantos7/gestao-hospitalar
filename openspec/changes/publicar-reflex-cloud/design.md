# Design

## Decisions

### CORS por variável de ambiente

O `rxconfig.py` fixava quatro origens locais, o que bloquearia o frontend publicado
em outro endereço. `origens_cors(GESTAO_CORS_ORIGINS)` mantém o padrão local e
aceita lista (barra final removida) ou `*`, que é o comportamento padrão do próprio
Reflex. A função é pura e fica fora do `rxconfig.py` para ser testada.

### Log sem disco

`get_logger` tenta o arquivo rotativo e, se o caminho for `-` ou a criação falhar com
`OSError`, usa `StreamHandler(stderr)`: na nuvem os logs aparecem no painel e um
sistema de arquivos somente leitura não impede o app de subir.

### Segredos

O padrão de `envfile` do `cloud.yml` é `.env`, que no desenvolvimento guarda
`XANO_TEST_*`. O `cloud.yml` fixa `.env.cloud` e o guia manda excluir `.env` do
pacote do backend (`--exclude-from-backend .env`). Testes garantem o `envfile`, o
`.gitignore` e a ausência de credenciais no modelo `.env.cloud.example`.

### Plano Free e região

O Free publica 1 app público e usa a região padrão; região (`gru`), app privado e
acesso restrito são do plano Pro. Os dados são fictícios, então o app público é
aceitável; o login do Xano continua protegendo as telas.

## Risks

- O comportamento exato do Reflex Cloud (CORS efetivo, `.env` ausente com
  `env_file=".env"`, política do plano Free) só se confirma no primeiro deploy.
- Uma instância só: o estado fica em memória e um novo deploy derruba as sessões.
