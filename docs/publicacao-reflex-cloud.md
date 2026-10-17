# Publicação no Reflex Cloud

Guia para publicar o sistema numa URL pública (HTTPS) para testadores externos.
**Use somente dados fictícios e contas de teste do Xano.** O deploy deve ser feito
de uma máquina pessoal, não da máquina corporativa.

## Antes de começar

- Conta no Reflex Cloud (`reflex login`). O plano Free publica 1 app público, com
  uso gratuito limitado; escolher região (ex.: `gru`, São Paulo), app privado,
  acesso restrito a usuários e domínio próprio exigem o plano Pro. Confira os
  planos em <https://reflex.dev/pricing/>, que podem mudar.
- Projeto com o `.venv` criado (`reflex` e `reflex-hosting-cli` já estão no
  `requirements.txt`). A CLI de nuvem **recusa-se a rodar** quando existe versão
  mais recente no PyPI — ela encerra com erro em vez de só avisar. Se aparecer
  `Warning: You are using reflex-hosting-cli version X...`, rode
  `pip install --upgrade reflex-hosting-cli` e fixe a nova versão no
  `requirements.txt` antes de continuar.
- Contas dedicadas de teste no Xano (uma por papel) e nenhum dado real.

## Passo a passo

1. Copie o modelo e ajuste só o que for necessário:

   ```powershell
   Copy-Item .env.cloud.example .env.cloud
   ```

   - `XANO_API_URL`: URL pública do grupo de API.
   - `GESTAO_CORS_ORIGINS`: `*` no primeiro teste; depois o endereço do app, por
     exemplo `https://SEU-APP.reflex.dev`.
   - `GESTAO_LOG_FILE=-`: logs na saída padrão (aparecem no painel da nuvem).
   - Ajuste `XANO_LIMITE_REQUISICOES` e `XANO_JANELA_SEGUNDOS` ao plano do Xano.
     Os testadores simultâneos dividem a mesma cota (o limite é por processo).

2. **Não envie o `.env` local.** O `cloud.yml` já aponta para `.env.cloud`, e o
   comando abaixo ainda exclui o `.env` do pacote do backend por garantia:

   ```powershell
   .\.venv\Scripts\python.exe -m reflex login
   .\.venv\Scripts\python.exe -m reflex deploy --envfile .env.cloud --exclude-from-backend .env
   ```

   O `reflex login` é interativo: ele abre o navegador e **espera você teclar
   `Enter` no terminal** depois de autenticar. Cada execução gera um
   `request_id` próprio, então use a URL impressa naquela execução — autenticar
   numa URL de outra tentativa deixa a CLI esperando um token que não vem.
   Confirme com `reflex cloud whoami`; o token fica em
   `%LOCALAPPDATA%\reflex\hosting_v1.json` e não deve ser versionado.

   Opcional: `--hostname seuapp` (endereço `seuapp.reflex.dev`) e, no plano Pro,
   `--region gru`.

3. Abra a URL que o comando mostrar e confira: login, Painel, uma lista, o botão
   de ajuda e o carregamento dos gráficos.

4. Se o navegador acusar erro de conexão com o backend, o primeiro suspeito é o
   CORS: ajuste `GESTAO_CORS_ORIGINS` e atualize os segredos:

   ```powershell
   .\.venv\Scripts\python.exe -m reflex cloud secrets update <APP_ID> --envfile .env.cloud --reboot
   ```

## Atualizar, acompanhar e remover

- **Atualizar (deploy já existente, já logado):** basta rodar de novo, de dentro
  do projeto:

  ```powershell
  .\.venv\Scripts\python.exe -m reflex deploy --envfile .env.cloud --exclude-from-backend .env
  ```

  Não é preciso logar de novo nem recriar o `.env.cloud` — a CLI reconhece o
  app pelo `cloud.yml` e pelo projeto já selecionado (`reflex cloud project
  selected`). Só repita o login se aparecer erro de token expirado/projeto não
  encontrado, ou atualize `GESTAO_CORS_ORIGINS`/outros valores e rode
  `reflex cloud secrets update <APP_ID> --envfile .env.cloud --reboot` quando
  só as variáveis mudarem (sem mudar código).
- Acompanhar um deploy em andamento:
  `reflex cloud apps status <ID_MOSTRADO_NO_DEPLOY> --watch`.
- Listar, ver logs e remover apps: `reflex cloud apps --help` (ou o painel web do
  Reflex Cloud).
- Revisão de segurança do código: `reflex cloud scan` (opcional).

## Limites e cuidados

- Uma instância só: o estado do Reflex fica em memória, então reiniciar ou
  redeployar derruba as sessões (os testadores entram de novo).
- O Free pode ter latência maior (região padrão `sjc`, EUA) e uso limitado.
- Mantenha o Xano com poucas contas de teste e troque as senhas ao encerrar os testes.
- Nunca coloque senhas, `XANO_TEST_*` ou tokens pessoais no `.env.cloud`.
- Para o caminho alternativo com Docker, ver o estudo de portabilidade (etapa 4 do roadmap).
