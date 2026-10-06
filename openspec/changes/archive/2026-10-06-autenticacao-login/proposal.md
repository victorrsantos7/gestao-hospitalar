# Proposal

## Why

Hoje a aplicação Reflex abre diretamente na página padrão de boas-vindas do
framework, sem nenhum controle de acesso. O sistema precisa de uma tela de
login para que apenas usuários autenticados (recepcionistas, médicos, equipe
de enfermagem/gestão) acessem as funcionalidades do hospital, e para que
mudanças futuras (cadastro de pacientes, atendimentos, internações etc.)
possam presumir um usuário autenticado e, futuramente, restringir ações por
papel.

## What Changes

- Adicionar uma página de login (`/`) como ponto de entrada da
  aplicação, substituindo a página padrão de boas-vindas gerada pelo
  `reflex init`.
- Criar um modelo de usuário do sistema (funcionário do hospital) com
  credenciais (login e senha com hash) e papel de acesso (recepcionista,
  médico, enfermagem/gestão).
- Implementar autenticação via `rx.State`: validação de credenciais,
  estabelecimento de sessão e redirecionamento após login bem-sucedido.
- Exibir mensagem de erro para credenciais inválidas, sem indicar qual campo
  está incorreto.
- Adicionar ação de logout, encerrando a sessão do usuário.
- Proteger o acesso a páginas internas (a serem criadas em changes futuras)
  exigindo sessão autenticada válida.

## Capabilities

### New Capabilities

- `autenticacao`: login, sessão do usuário autenticado, logout e proteção de
  páginas internas contra acesso não autenticado.

### Modified Capabilities

(nenhuma — não há specs existentes no projeto)

## Impact

- Nova dependência `bcrypt` em `requirements.txt` para hash de senha.
- Novo modelo `Usuario` (`rx.Model`) e migração de banco correspondente.
- Novo `AuthState` (`rx.State`) responsável pela lógica de autenticação,
  guardando apenas `usuario_id` e `papel` do usuário autenticado.
- Nova página `login.py` em `gestao_hospitalar/`, substituindo a página
  `index` padrão do template em branco do Reflex.
- Nova página `dashboard.py` (placeholder) como destino pós-login e exemplo
  de página interna protegida.
- Novo script `seed.py` para criação manual do usuário administrador
  inicial (login/senha fixos de desenvolvimento).
- `docs/domain-model.md` ainda não possui a entidade "Usuário do sistema"
  (login/papel de acesso) — precisa ser complementado nesta change, pois é
  um conceito de domínio novo, distinto de Paciente/Médico/Convênio.
