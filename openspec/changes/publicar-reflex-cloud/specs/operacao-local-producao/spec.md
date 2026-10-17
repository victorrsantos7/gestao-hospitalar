# operacao-local-producao Specification

## ADDED Requirements

### Requirement: Origens e logs configuráveis para implantação

O sistema MUST permitir definir as origens aceitas pelo backend por variável de
ambiente, mantendo apenas as portas locais de desenvolvimento quando ela não
existir, e MUST permitir enviar os logs para a saída padrão sem falhar quando a
pasta de logs não puder ser escrita.

#### Scenario: Sem configuração

- **WHEN** `GESTAO_CORS_ORIGINS` não está definida
- **THEN** só `localhost` e `127.0.0.1` nas portas 3000 e 3001 são aceitos

#### Scenario: App publicado

- **WHEN** `GESTAO_CORS_ORIGINS` lista o endereço do app
- **THEN** o backend aceita essas origens no lugar das locais

#### Scenario: Pasta de logs sem escrita

- **WHEN** o arquivo de log não pode ser criado
- **THEN** o sistema inicia e grava os logs na saída padrão
