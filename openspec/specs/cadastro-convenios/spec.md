# cadastro-convenios Specification

## Purpose
Permite manter convênios consistentes e protegidos para que sejam utilizados
nos atendimentos e no histórico da jornada do paciente.

## Requirements

### Requirement: Cadastro e manutenção de convênios

O sistema MUST permitir que usuários autorizados criem, consultem, atualizem
e excluam convênios com nome, tipo e cobertura, mantendo o nome normalizado
único.

#### Scenario: Cadastro válido de convênio

- **WHEN** um usuário autorizado informa nome, tipo permitido e cobertura
- **THEN** o sistema cria o convênio, confirma o identificador gerado e
  disponibiliza o registro na consulta

#### Scenario: Tipo de convênio inválido

- **WHEN** um usuário envia um tipo diferente de `particular`, `plano` ou `SUS`
- **THEN** o sistema rejeita a operação e informa que o tipo é inválido

#### Scenario: Nome de convênio duplicado

- **WHEN** um usuário tenta criar ou atualizar um convênio com nome já
  cadastrado após normalização
- **THEN** o sistema rejeita a operação e informa que o convênio já está
  cadastrado

#### Scenario: Atualização de convênio

- **WHEN** um usuário autorizado envia dados válidos para um convênio
  existente
- **THEN** o sistema atualiza o registro e exibe os dados atuais na consulta

#### Scenario: Exclusão de convênio

- **WHEN** um usuário autorizado solicita a exclusão de um convênio existente
- **THEN** o sistema remove o registro somente após confirmação do serviço
  remoto e atualiza a listagem

### Requirement: Consulta de convênios

O sistema MUST permitir listar convênios e consultar seus detalhes para
usuários autenticados com o recurso `convenios`.

#### Scenario: Usuário autorizado consulta convênios

- **WHEN** um usuário com permissão abre a área de convênios
- **THEN** o sistema exibe os convênios cadastrados e permite consultar nome,
  tipo e cobertura

#### Scenario: Serviço de convênios indisponível

- **WHEN** a consulta ou manutenção não pode ser concluída no serviço remoto
- **THEN** o sistema mantém a sessão, não exibe dados parcialmente confirmados
  e informa uma falha genérica

### Requirement: Autorização de convênios

O backend MUST permitir consulta e manutenção de convênios somente para papéis
com o recurso `convenios` na matriz fixa, rejeitando chamadas diretas de papéis
sem permissão.

#### Scenario: Papel autorizado mantém convênio

- **WHEN** recepcionista ou admin envia uma operação válida de convênio
- **THEN** o backend permite a operação após autenticar o token

#### Scenario: Papel sem permissão tenta acessar convênios

- **WHEN** médico ou enfermagem/gestão tenta consultar ou alterar convênios
- **THEN** o backend rejeita a operação e não expõe os registros protegidos
