# Tasks

- [x] 1. Criar tabela `convenios` no Xano com nome normalizado único, tipo,
      cobertura e endpoints autenticados de listagem, consulta, criação,
      atualização e exclusão. Tabela publicada no Xano com índice único em
      `nome_normalizado`; os endpoints foram configurados com autenticação.
- [x] 2. Adicionar ao cliente Xano os contratos de convênios, validação das
      respostas e tratamento de conflitos e falhas.
- [x] 3. Implementar no `AuthState` os campos, setters, validações, eventos,
      carregamento e autorização do cadastro de convênios.
- [x] 4. Criar a tela Reflex `/convenios` com formulário, seleção de tipo,
      listagem, detalhes e ações de manutenção, mantendo o visual atual.
- [x] 5. Registrar a rota protegida e adicionar o acesso de convênios no
      dashboard conforme a permissão do usuário.
- [x] 6. Adicionar testes unitários para cliente, validação, autorização e
      fluxo do estado, incluindo papéis permitidos e negados.
- [x] 7. Executar testes, `reflex compile --dry`, validação OpenSpec e
      validação manual dos endpoints publicados no Xano. Testes, compilação e
      OpenSpec passaram; tabela, índice e cinco endpoints privados foram
      publicados no ambiente live.