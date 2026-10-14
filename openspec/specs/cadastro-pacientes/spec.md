# cadastro-pacientes Specification

## Purpose

Permitir que o hospital registre e consulte pacientes com CPF único, dados
obrigatórios validados e proteção de informações pessoais desde o backend.

## Requirements

### Requirement: Cadastro de paciente autorizado

O sistema MUST permitir que recepcionista ou admin cadastre, edite e exclua um
paciente com nome, CPF, data de nascimento, telefone, endereço e contato de
emergência, e MUST validar a entrada no backend em todas as operações. A
interface MUST aceitar somente caracteres compatíveis com cada campo, exibir
máscara para CPF e telefones e preservar os dados normalizados antes do envio
ao Xano.

#### Scenario: Cadastro válido
- **WHEN** recepcionista ou admin envia todos os campos obrigatórios com CPF
  válido e ainda não cadastrado
- **THEN** o sistema cria o paciente e retorna seu identificador sem expor
  dados de outros pacientes

#### Scenario: Usuário sem permissão tenta cadastrar
- **WHEN** médico ou enfermagem/gestão tenta criar um paciente
- **THEN** o backend rejeita a operação e não grava dados

#### Scenario: Nome com formato inválido
- **WHEN** um usuário autorizado informa números no nome do paciente
- **THEN** o sistema rejeita o cadastro e informa erro de validação sem criar
  registro

#### Scenario: Telefone fora do padrão brasileiro
- **WHEN** um usuário autorizado informa telefone ou contato de emergência com
  quantidade diferente de 10 ou 11 dígitos
- **THEN** o sistema rejeita o cadastro e informa erro de validação sem criar
  registro

#### Scenario: Data de nascimento inválida
- **WHEN** um usuário autorizado informa data inexistente ou posterior à data
  atual
- **THEN** o sistema rejeita o cadastro e informa erro de validação sem criar
  registro

#### Scenario: Máscara e normalização dos campos
- **WHEN** um usuário autorizado preenche CPF, telefone ou contato de
  emergência usando a máscara visual permitida
- **THEN** o sistema exibe a formatação correspondente e envia ao backend
  somente os dígitos normalizados

#### Scenario: Edição válida de paciente
- **WHEN** recepcionista ou admin seleciona um paciente existente e envia
  dados válidos e completos para edição
- **THEN** o sistema atualiza o registro no backend e exibe os dados
  atualizados na listagem e nos detalhes

#### Scenario: Edição com CPF duplicado
- **WHEN** recepcionista ou admin edita um paciente informando um CPF já
  usado por outro paciente
- **THEN** o sistema rejeita a atualização e informa que o CPF já está
  cadastrado, sem alterar o registro original

#### Scenario: Exclusão de paciente autorizada
- **WHEN** recepcionista ou admin solicita a exclusão de um paciente existente
- **THEN** o sistema remove o registro somente após confirmação do serviço
  remoto e atualiza a listagem

#### Scenario: Usuário sem permissão tenta editar ou excluir
- **WHEN** médico ou enfermagem/gestão tenta editar ou excluir um paciente
- **THEN** o backend rejeita a operação e não altera nem remove dados

### Requirement: CPF único e válido

O sistema MUST rejeitar CPF ausente, inválido ou já cadastrado, considerando
apenas os dígitos para validação e comparação de unicidade.

#### Scenario: CPF inválido
- **WHEN** um usuário autorizado envia CPF com quantidade ou dígitos
  verificadores inválidos
- **THEN** o sistema rejeita o cadastro e informa erro de validação sem criar
  registro

#### Scenario: CPF duplicado
- **WHEN** um usuário autorizado envia CPF já existente após normalização
- **THEN** o sistema rejeita o cadastro e informa que o CPF já está cadastrado

### Requirement: Consulta de pacientes autorizada

O sistema MUST permitir que recepcionista, médico e admin consultem pacientes, e
MUST impedir que enfermagem/gestão consulte a listagem cadastral nesta etapa,
conforme a matriz fixa de papéis.

#### Scenario: Listagem permitida
- **WHEN** recepcionista, médico ou admin solicita a listagem
- **THEN** o sistema retorna pacientes sem incluir senha ou campos internos

#### Scenario: Listagem negada
- **WHEN** enfermagem/gestão solicita a listagem de pacientes
- **THEN** o backend rejeita a operação sem retornar dados cadastrais

### Requirement: Protecao de dados pessoais

O sistema MUST exigir autenticação e autorização no backend para todas as
operações de pacientes e MUST evitar que contato de emergência seja exposto na
listagem resumida.

#### Scenario: Acesso sem sessão
- **WHEN** uma pessoa sem sessão válida tenta consultar ou cadastrar paciente
- **THEN** o sistema rejeita a operação e não retorna dados pessoais

#### Scenario: Consulta detalhada autorizada
- **WHEN** um usuário autorizado solicita um paciente específico
- **THEN** o sistema retorna os dados necessários ao atendimento, incluindo
  contato de emergência apenas na consulta detalhada
