# publicacao-nuvem Specification

## ADDED Requirements

### Requirement: Publicação sem vazar credenciais locais

O projeto MUST fornecer um arquivo de configuração de implantação que aponte para
um arquivo de variáveis específico da nuvem, MUST manter esse arquivo e o `.env`
fora do controle de versão e MUST NOT incluir credenciais de teste nem tokens
pessoais no modelo desse arquivo.

#### Scenario: Deploy com a configuração do projeto

- **WHEN** o deploy é feito com o `cloud.yml` do projeto
- **THEN** as variáveis enviadas vêm de `.env.cloud`, não do `.env` local

#### Scenario: Modelo de variáveis da nuvem

- **WHEN** alguém copia `.env.cloud.example`
- **THEN** o modelo não contém `XANO_TEST_*` nem `XANO_API_TOKEN` preenchidos

### Requirement: Guia de publicação

A documentação MUST descrever como publicar e atualizar o app no Reflex Cloud,
os limites do plano gratuito e que apenas dados fictícios devem ser usados.

#### Scenario: Primeira publicação

- **WHEN** a pessoa segue `docs/publicacao-reflex-cloud.md`
- **THEN** obtém o app numa URL pública sem enviar o `.env` local
