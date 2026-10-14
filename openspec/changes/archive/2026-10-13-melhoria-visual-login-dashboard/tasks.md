# Tasks

## 1. Login visual

- [x] 1.1 Reorganizar a composição visual da tela de login em painel hospitalar e formulário atual; verificar que bindings, textos, evento e erros permanecem iguais.
- [x] 1.2 Aplicar imagem, cores, tipografia, espaçamento e responsividade sem alterar comportamento; verificar desktop e mobile.

## 2. Dashboard visual

- [x] 2.1 Reorganizar visualmente o dashboard e os acessos existentes sem criar novas ações; verificar todas as rotas atuais.
- [x] 2.2 Validar a visibilidade dos acessos para recepcionista, médico, enfermagem/gestão e admin; confirmar que a matriz não mudou.

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate melhoria-visual-login-dashboard --strict`.
- [x] 3.2 Executar validação visual local em desktop/mobile e confirmar login válido, login inválido, logout, rotas e permissões sem regressão.
