# Proposal

## Why

A persistencia atual esta acoplada ao SQLite por meio de `rx.session()` e
SQLModel, mas o grupo decidiu adotar o Xano como backend de dados. Esta
mudanca precisa ser especificada antes da implementacao porque altera a
arquitetura de acesso a dados, a configuracao de ambiente e o caminho usado
pela autenticacao.

## What Changes

- Criar uma camada de integracao com a API do Xano para leitura e escrita de
  dados do sistema.
- Substituir o acesso direto ao banco local nos fluxos abrangidos pela
  integracao por chamadas ao Xano.
- Definir configuracao por variaveis de ambiente para URL da API e, quando o
  grupo estiver protegido, credenciais adicionais, sem armazenar segredos no
  repositorio.
- Definir tratamento de indisponibilidade, erros HTTP e respostas invalidas do
  Xano.
- Adaptar o login para o endpoint de autenticacao do Xano, mantendo a senha
  protegida exclusivamente no recurso de autenticacao remoto e retornando para
  a aplicacao somente os dados publicos da sessao.
- Documentar a transicao e os limites da primeira etapa de integracao.
- **BREAKING**: deixar de considerar SQLite/SQLModel como persistencia principal
  da aplicacao nos fluxos migrados.

Fora do escopo desta change: cadastro de pacientes, autorizacao por papel,
RBAC, telas de dashboard, financeiro e relatorios, alem da modelagem completa
de todos os modulos do dominio.

## Capabilities

### New Capabilities

- `persistencia-xano`: contrato para configuracao, comunicacao segura e
  tratamento de falhas na persistencia via API do Xano.

### Modified Capabilities

Nenhuma. A autenticacao existente tera sua implementacao adaptada, mas seus
requisitos funcionais de login, sessao e logout permanecem os mesmos. A
protecao e a verificacao da senha ficam sob responsabilidade do Xano.

## Impact

- `gestao_hospitalar/models.py`: acesso atual via SQLModel devera ser isolado
  ou substituido nos fluxos migrados.
- `gestao_hospitalar/auth_state.py`: login devera consultar o Xano sem expor
  credenciais ou alterar o comportamento funcional da autenticacao.
- `rxconfig.py` e configuracao de ambiente: remover a dependencia operacional
  do `db_url` local nos fluxos migrados e adicionar configuracoes do Xano.
- `requirements.txt`: avaliar o cliente HTTP existente ou uma dependencia
  especifica, evitando dependencias desnecessarias.
- Ambiente Xano: exigir endpoint, autenticacao da API e contrato das tabelas
  ou endpoints utilizados.
- Testes: cobrir sucesso, erro de autenticacao, indisponibilidade, timeout e
  resposta invalida da API.
