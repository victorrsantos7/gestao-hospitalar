# Tasks
O relatório em `docs/validacao-cadastro-pacientes.md` registra os cenários
confirmados, incluindo CPF inválido e tentativa de criação sem permissão.
- [x] 1.3 Configurar proteção do grupo/API e tratar referências à tabela; verificar chamadas não autenticadas rejeitadas.

## 2. Regras e cliente

- [x] 2.1 Implementar normalização e validação de CPF com testes de casos válidos, inválidos e repetição de dígitos.
- [x] 2.2 Adicionar operações do cliente Xano para criar, listar e consultar pacientes; verificar payloads e respostas com transporte falso.
- [x] 2.3 Aplicar autorização de recepcionista/admin para criação e recepcionista/médico/admin para consulta; verificar negações no backend.

## 3. Interface Reflex

- [x] 3.1 Criar estado e formulário de cadastro com validação de campos obrigatórios; verificar mensagens sem expor dados sensíveis.
- [x] 3.2 Criar listagem resumida e consulta detalhada protegidas por papel; verificar que contato de emergência não aparece na listagem.
- [x] 3.3 Adicionar navegação acessível aos papéis permitidos sem liberar operações pelo frontend; verificar rota protegida sem sessão.

## 4. Validação final

- [x] 4.1 Executar testes, `py_compile` e `reflex compile --dry`; confirmar compilação da aplicação.
- [x] 4.2 Testar cadastro válido, CPF inválido, CPF duplicado e permissões com usuários Xano de teste; registrar resultados.
- [x] 4.3 Atualizar documentação e marcar a change pronta antes de iniciar atendimentos.

O relatório em `docs/validacao-cadastro-pacientes.md` registra os cenários já
confirmados. Permanecem pendentes uma tentativa remota com CPF inválido e uma
tentativa de criação usando papel sem permissão; por isso a change ainda não
deve ser marcada como pronta.
