# Spec Delta

## MODIFIED Requirements

### Requirement: Cadastro de médicos

O sistema MUST permitir cadastrar, editar e excluir um médico com nome, CRM,
especialidade e telefone, validando os campos obrigatórios e mantendo o CRM
único em todas as operações.

#### Scenario: Cadastro válido de médico
- **WHEN** um usuário autorizado informa nome, CRM, especialidade e telefone válidos
- **THEN** o sistema cria o médico e confirma o cadastro sem expor dados de autenticação

#### Scenario: CRM duplicado
- **WHEN** um usuário tenta cadastrar um CRM já existente
- **THEN** o sistema rejeita o cadastro e informa que o CRM já está cadastrado

#### Scenario: Dados inválidos
- **WHEN** um usuário envia nome, CRM ou telefone inválido
- **THEN** o sistema rejeita o cadastro e informa o campo que precisa ser corrigido

#### Scenario: Edição válida de médico
- **WHEN** um usuário autorizado seleciona um médico existente e envia dados
  válidos e completos para edição
- **THEN** o sistema atualiza o registro no backend e exibe os dados
  atualizados na listagem e nos detalhes

#### Scenario: Edição com CRM duplicado
- **WHEN** um usuário autorizado edita um médico informando um CRM já usado
  por outro médico
- **THEN** o sistema rejeita a atualização e informa que o CRM já está
  cadastrado, sem alterar o registro original

#### Scenario: Exclusão de médico autorizada
- **WHEN** um usuário autorizado solicita a exclusão de um médico existente
- **THEN** o sistema remove o registro somente após confirmação do serviço
  remoto e atualiza a listagem

### Requirement: Autorização do cadastro de médicos

O backend MUST permitir leitura, criação, edição e exclusão de médicos somente
para papéis com o recurso `medicos` na matriz fixa, rejeitando chamadas
diretas de papéis sem permissão.

#### Scenario: Papel autorizado cria médico
- **WHEN** recepcionista ou admin envia um cadastro válido
- **THEN** o backend permite a criação do médico

#### Scenario: Papel sem permissão tenta consultar ou criar
- **WHEN** médico ou enfermagem/gestão tenta acessar ou alterar médicos sem o recurso autorizado
- **THEN** o backend rejeita a operação e não expõe os dados protegidos

#### Scenario: Papel sem permissão tenta editar ou excluir
- **WHEN** médico ou enfermagem/gestão tenta editar ou excluir um médico
  cadastrado
- **THEN** o backend rejeita a operação e não altera nem remove dados
