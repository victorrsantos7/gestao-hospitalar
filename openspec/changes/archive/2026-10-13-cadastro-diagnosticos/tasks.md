# Tasks

## 1. Persistência e API Xano

- [x] 1.1 Criar a tabela `diagnosticos` com atendimento, descrição, código CID e data, incluindo referência válida ao atendimento; verificar a estrutura publicada no Xano.
- [x] 1.2 Criar os endpoints privados de criação e consulta por atendimento, com preconditions para médico/admin e respostas sem dados internos; verificar chamadas autorizadas e negadas no ambiente live.

## 2. Cliente e validação

- [x] 2.1 Adicionar ao cliente Xano os métodos de criação e listagem de diagnósticos, normalização das respostas e tratamento de falhas sem limpar a sessão; verificar testes do contrato HTTP.
- [x] 2.2 Implementar validadores de referência, descrição, código CID e data; verificar casos válidos, campos vazios, data inválida e identificador inexistente.

## 3. Estado e interface Reflex

- [x] 3.1 Adicionar ao `AuthState` campos e eventos explícitos para formulário, listagem, mensagens e carregamento de diagnósticos; verificar autorização e preservação da sessão em falhas.
- [x] 3.2 Integrar a consulta de diagnósticos ao detalhe do atendimento e exibir o formulário apenas para médico/admin; verificar que recepcionista e enfermagem/gestão não recebem dados nem controles.

## 4. Testes e validação final

- [x] 4.1 Adicionar testes de autorização, validadores, `AuthState` e cliente Xano cobrindo criação, consulta, falhas e papéis bloqueados; verificar a suíte completa.
- [x] 4.2 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate cadastro-diagnosticos --strict`; confirmar todos os comandos sem erro.
- [x] 4.3 Realizar validação manual com médico, admin, recepcionista e enfermagem/gestão no ambiente live; confirmar registro, consulta, bloqueios e ausência de dados parciais antes do archive.
