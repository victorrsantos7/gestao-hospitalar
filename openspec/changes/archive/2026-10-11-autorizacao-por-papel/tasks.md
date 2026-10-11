# Tasks

## 1. Matriz e regras de backend

- [x] 1.1 Criar a matriz fixa dos quatro papéis e verificar por testes as permissões permitidas e negadas.
- [x] 1.2 Criar helper de autorização que valide sessão, papel conhecido e recurso solicitado; verificar negação por padrão.
- [x] 1.3 Garantir que papel desconhecido ou sessão ausente nunca receba acesso por fallback; verificar com testes unitários.

## 2. Sessão e navegação

- [x] 2.1 Aplicar a checagem de autorização à rota dashboard e ao redirecionamento pós-login; verificar cada papel com teste de navegação.
- [x] 2.2 Filtrar a navegação exibida conforme o papel sem depender dela para segurança; verificar que ações protegidas continuam rejeitadas no backend.
- [x] 2.3 Garantir que logout limpa papel e sessão; verificar retorno à página de login.

## 3. Integração e documentação

- [x] 3.1 Documentar a matriz fixa e a regra de inclusão de autorização nas próximas funcionalidades; verificar links e consistência com a spec.
- [x] 3.2 Executar testes, `py_compile` e `reflex compile --dry`; confirmar que a aplicação continua compilando.
- [x] 3.3 Validar manualmente login e acesso com os quatro papéis, incluindo uma tentativa negada; registrar o resultado antes de iniciar o cadastro de pacientes.
	- Validacao automatizada e manual confirmadas pelo usuario para os quatro papeis e uma tentativa negada.
