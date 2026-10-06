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
O sistema SHALL exigir uma sessão autenticada válida para exibir qualquer
página interna da aplicação, redirecionando para a página de login quando
não houver sessão válida.

#### Scenario: Acesso sem sessão autenticada
- **WHEN** um usuário sem sessão autenticada tenta acessar uma página interna
- **THEN** o sistema SHALL redirecioná-lo para a página de login

### Requirement: Logout encerra a sessão
O sistema SHALL permitir que o usuário autenticado encerre sua sessão
explicitamente.

#### Scenario: Logout
- **WHEN** um usuário autenticado aciona a opção de logout
- **THEN** o sistema SHALL encerrar a sessão e redirecionar o usuário para a
  página de login
