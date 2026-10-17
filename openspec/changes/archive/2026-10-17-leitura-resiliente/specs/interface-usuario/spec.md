# interface-usuario Specification

## ADDED Requirements

### Requirement: Nova tentativa após falha de leitura

Quando a leitura inicial de uma tela falhar por indisponibilidade do Xano, a
interface MUST exibir o aviso de erro com a ação "Tentar novamente", que repete
a leitura da tela atual com indicador de carregamento, mantendo na tela os
últimos dados lidos. O aviso MUST NOT oferecer a ação depois que uma nova
leitura de página começar.

#### Scenario: Falha ao carregar uma lista

- **WHEN** a leitura de pacientes falha por indisponibilidade
- **THEN** o aviso mostra a mensagem e o botão "Tentar novamente"

#### Scenario: Repetir a leitura

- **WHEN** a pessoa aciona "Tentar novamente"
- **THEN** a leitura da tela atual é repetida e o botão mostra carregamento até o fim

#### Scenario: Erro de escrita

- **WHEN** o cadastro de um registro falha
- **THEN** o aviso é exibido sem a ação de repetir a leitura

### Requirement: Sessão expirada leva ao login

Quando o Xano recusar o token da sessão durante uma leitura, a interface MUST
avisar que a sessão expirou e encerrar a sessão, levando a pessoa ao login, em
vez de mostrar a mensagem genérica de falha.

#### Scenario: Token recusado ao abrir uma tela

- **WHEN** a leitura inicial de uma tela recebe 401 do Xano
- **THEN** aparece o aviso "Sua sessão expirou. Entre novamente." e a pessoa é levada ao login
