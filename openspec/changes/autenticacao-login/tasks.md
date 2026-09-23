# Tasks

## 1. Modelo de dados

- [ ] 1.1 Criar o modelo `Usuario` (`rx.Model`) com campos `login` (único),
      `senha_hash` e `papel`, e verificar que a tabela é criada via
      `reflex db migrate`
- [ ] 1.2 Criar script/seed de um usuário administrador inicial e verificar
      que ele consegue autenticar com a senha definida

## 2. Autenticação (backend)

- [ ] 2.1 Implementar `AuthState` com evento de login: validar login/senha
      (comparando hash), definir usuário autenticado em caso de sucesso e
      verificar que credenciais corretas autenticam
- [ ] 2.2 Implementar rejeição de credenciais inválidas com mensagem de erro
      genérica e verificar que login/senha incorretos não autenticam nem
      revelam qual campo está errado
- [ ] 2.3 Implementar evento de logout que encerra a sessão e verificar que,
      após logout, o usuário deixa de ser considerado autenticado

## 3. Páginas (frontend)

- [ ] 3.1 Criar a página `login.py` com formulário de login (campos login e
      senha, botão de entrar, exibição de mensagem de erro) e verificar que
      ela renderiza na rota `/`
- [ ] 3.2 Substituir a página `index` padrão do template em branco pela
      página de login e verificar que `reflex run` abre a tela de login em
      vez da página de boas-vindas do Reflex
- [ ] 3.3 Adicionar redirecionamento para a página inicial da aplicação após
      login bem-sucedido e verificar o comportamento manualmente

## 4. Proteção de páginas internas

- [ ] 4.1 Implementar verificação de sessão autenticada (`on_load` ou
      equivalente) reutilizável para páginas internas e verificar que uma
      página interna de teste redireciona para `/login` quando não há
      sessão
- [ ] 4.2 Adicionar ação de logout acessível a partir de uma página interna
      e verificar que ela retorna o usuário para a página de login

## 5. Documentação

- [ ] 5.1 Atualizar `docs/domain-model.md` incluindo a entidade "Usuário do
      sistema" (login, papel) e verificar que o documento reflete o modelo
      implementado
