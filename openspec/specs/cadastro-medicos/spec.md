# cadastro-medicos Specification

## Purpose
Permite manter médicos identificados por CRM e disponibilizá-los para os
fluxos de atendimento, com dados consistentes e acesso protegido por papel.

## Requirements

### Requirement: Cadastro de médicos

O sistema MUST permitir cadastrar um médico com nome, CRM, especialidade e
telefone, validando os campos obrigatórios e mantendo o CRM único.

#### Scenario: Cadastro válido de médico
- **WHEN** um usuário autorizado informa nome, CRM, especialidade e telefone válidos
- **THEN** o sistema cria o médico e confirma o cadastro sem expor dados de autenticação

#### Scenario: CRM duplicado
- **WHEN** um usuário tenta cadastrar um CRM já existente
- **THEN** o sistema rejeita o cadastro e informa que o CRM já está cadastrado

#### Scenario: Dados inválidos
- **WHEN** um usuário envia nome, CRM ou telefone inválido
- **THEN** o sistema rejeita o cadastro e informa o campo que precisa ser corrigido

### Requirement: Consulta de médicos

O sistema MUST permitir listar e consultar detalhes dos médicos cadastrados para
usuários com permissão de acesso ao recurso `medicos`.

#### Scenario: Usuário autorizado consulta médicos
- **WHEN** um usuário autorizado abre a área de médicos
- **THEN** o sistema exibe a lista e permite consultar os detalhes de um médico

#### Scenario: Falha no serviço de médicos
- **WHEN** a consulta não pode ser concluída no serviço remoto
- **THEN** o sistema mantém a sessão e exibe uma mensagem genérica de falha

### Requirement: Autorização do cadastro de médicos

O backend MUST permitir leitura e criação de médicos somente para papéis com o
recurso `medicos` na matriz fixa, rejeitando chamadas diretas de papéis sem
permissão.

#### Scenario: Papel autorizado cria médico
- **WHEN** recepcionista ou admin envia um cadastro válido
- **THEN** o backend permite a criação do médico

#### Scenario: Papel sem permissão tenta consultar ou criar
- **WHEN** médico ou enfermagem/gestão tenta acessar ou alterar médicos sem o recurso autorizado
- **THEN** o backend rejeita a operação e não expõe os dados protegidos
