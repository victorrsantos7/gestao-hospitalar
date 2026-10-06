# Tasks

## 1. Modelo de dados

- [x] 1.1 Adicionar `bcrypt` a `requirements.txt` e instalar no ambiente
- [x] 1.2 Criar o modelo `Usuario` (`SQLModel`, não `rx.Model` — deprecated
      desde Reflex 0.9.2) com campos `login` (único), `senha_hash` e
      `papel`, e verificar que a tabela é criada via `reflex db init`
      (detectou o modelo e já gerou a migração inicial) seguido de
      `reflex db migrate`
- [x] 1.3 Criar script `gestao_hospitalar/seed.py` que insere um usuário
      administrador inicial (login/senha fixos de desenvolvimento,
      documentados no README), executável manualmente via
      `python -m gestao_hospitalar.seed`, e verificar que ele é idempotente
      (não duplica o usuário ao rodar novamente)

## 2. Autenticação (backend)

- [x] 2.1 Implementar `AuthState` com `usuario_id` e `papel` (não o objeto
      `Usuario` completo) e computed var `is_authenticated`
- [x] 2.2 Implementar evento de login: validar login/senha (comparando hash
      com `bcrypt`), preencher `usuario_id`/`papel` em caso de sucesso e
      verificar que credenciais corretas autenticam
- [x] 2.3 Implementar rejeição de credenciais inválidas com mensagem de erro
      genérica e verificar que login/senha incorretos não autenticam nem
      revelam qual campo está errado
- [x] 2.4 Implementar evento de logout que limpa `usuario_id`/`papel` e
      verifica que, após logout, o usuário deixa de ser considerado
      autenticado

## 3. Páginas (frontend)

- [x] 3.1 Criar a página `login.py` com formulário de login (campos login e
      senha, botão de entrar, exibição de mensagem de erro) e verificar que
      ela renderiza na rota `/`
- [x] 3.2 Substituir a página `index` padrão do template em branco pela
      página de login e verificar que `reflex run` abre a tela de login em
      vez da página de boas-vindas do Reflex
- [x] 3.3 Criar página `dashboard.py` placeholder (mensagem de boas-vindas,
      nome do usuário autenticado e botão de logout) na rota `/dashboard`
- [x] 3.4 Adicionar redirecionamento para `/dashboard` após login
      bem-sucedido e verificar o comportamento manualmente

## 4. Proteção de páginas internas

- [x] 4.1 Implementar verificação de sessão autenticada (`on_load` ou
      equivalente) reutilizável para páginas internas e verificar que a
      página `/dashboard` redireciona para `/` (página de login) quando não
      há sessão
- [x] 4.2 Adicionar ação de logout ao botão da página `/dashboard` e
      verificar que ela retorna o usuário para a página de login

## 5. Documentação

- [x] 5.1 Atualizar `docs/domain-model.md` incluindo a entidade "Usuário do
      sistema" (login, papel) e verificar que o documento reflete o modelo
      implementado
