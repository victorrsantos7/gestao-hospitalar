# Autenticacao Specification

## Purpose

Garante que apenas usuários autenticados do hospital acessem as
funcionalidades internas do sistema, por meio de login, sessão e logout.

## Requirements

### Requirement: Autenticação por login e senha
O sistema SHALL permitir que um usuário cadastrado se autentique informando
login e senha na página de login.

#### Scenario: Login com credenciais válidas
- **WHEN** um usuário cadastrado informa login e senha corretos na página de
  login
- **THEN** o sistema SHALL estabelecer uma sessão autenticada e redirecionar
  o usuário para a página inicial da aplicação

#### Scenario: Login com credenciais inválidas
- **WHEN** um usuário informa login ou senha incorretos
- **THEN** o sistema SHALL rejeitar a tentativa e exibir uma mensagem de erro
  genérica, sem indicar se o login ou a senha estão incorretos

### Requirement: Senhas armazenadas com hash
O sistema SHALL armazenar a senha do usuário apenas na forma de hash, nunca
em texto aberto.

#### Scenario: Definição de senha
- **WHEN** uma senha é definida ou atualizada para um usuário
- **THEN** o sistema SHALL persistir apenas o hash da senha, nunca o valor
  original

### Requirement: Proteção de páginas internas

O sistema SHALL exigir uma sessão autenticada válida e um papel autorizado
para exibir ou executar qualquer funcionalidade interna da aplicação,
redirecionando para a página de login quando não houver sessão válida e
rejeitando no backend quando o papel não tiver permissão.

#### Scenario: Acesso sem sessão autenticada
- **WHEN** um usuário sem sessão autenticada tenta acessar uma página interna
- **THEN** o sistema SHALL redirecioná-lo para a página de login

#### Scenario: Sessão válida sem permissão
- **WHEN** um usuário autenticado tenta acessar uma página fora das permissões
  de seu papel
- **THEN** o sistema SHALL rejeitar o acesso no backend e redirecionar para
  uma área permitida ou exibir acesso negado

### Requirement: Logout encerra a sessão
O sistema SHALL permitir que o usuário autenticado encerre sua sessão
explicitamente.

#### Scenario: Logout
- **WHEN** um usuário autenticado aciona a opção de logout
- **THEN** o sistema SHALL encerrar a sessão e redirecionar o usuário para a
  página de login

### Requirement: Autorizacao fixa por papel

O sistema MUST aplicar no backend a matriz fixa de permissões abaixo:

- `recepcionista`: pacientes, médicos, convênios e atendimentos.
- `medico`: visualização de pacientes e atendimentos, além de registro de
  diagnósticos.
- `enfermagem_gestao`: internações, leitos, transferências e histórico.
- `admin`: todas as funcionalidades e gerenciamento de usuários.

#### Scenario: Papel permitido acessa a funcionalidade
- **WHEN** um usuário autenticado tenta acessar uma funcionalidade permitida
  para seu papel
- **THEN** o backend permite a operação e a interface apresenta a área
  correspondente

#### Scenario: Papel sem permissão tenta acessar a funcionalidade
- **WHEN** um usuário autenticado tenta acessar uma funcionalidade fora da
  matriz de seu papel
- **THEN** o backend rejeita a operação e não expõe os dados protegidos

#### Scenario: Papel desconhecido tenta acessar área interna
- **WHEN** uma sessão autenticada contém um papel que não está na matriz fixa
- **THEN** o sistema rejeita o acesso protegido e não concede permissões por
  padrão

### Requirement: Navegação inicial por papel

O sistema MUST encaminhar o usuário autenticado para uma home compatível com
seu papel. Gestão/admin MUST ter acesso à visão consolidada de dashboard,
financeiro e relatórios quando essas áreas estiverem disponíveis.

#### Scenario: Usuário entra com papel operacional
- **WHEN** recepcionista, médico ou enfermagem/gestão conclui o login
- **THEN** o sistema redireciona para a home do papel sem exibir áreas não
  autorizadas

#### Scenario: Usuário entra como admin
- **WHEN** admin conclui o login
- **THEN** o sistema redireciona para a visão administrativa com acesso total
  às funcionalidades disponíveis
