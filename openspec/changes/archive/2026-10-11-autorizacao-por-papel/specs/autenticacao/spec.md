# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
