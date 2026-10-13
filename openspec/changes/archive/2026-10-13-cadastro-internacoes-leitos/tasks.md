# Tasks

## 1. Persistência e API Xano

- [x] 1.1 Criar a tabela `leitos` com número único e status controlado; verificar schema, índice e status inicial `livre` no Xano.
- [x] 1.2 Criar a tabela `internacoes` com referências a atendimento, paciente e leito, datas e status; verificar referências e índices no Xano.
- [x] 1.3 Criar endpoints privados de leitos para cadastro e listagem com preconditions de enfermagem/gestão ou admin; verificar papéis autorizados e negados no ambiente live.
- [x] 1.4 Criar endpoints privados de internação, consulta e alta com validações de atendimento, leito, datas e ocupação exclusiva; verificar criação, alta e ausência de alterações parciais no ambiente live.
- [x] 1.5 Criar endpoint privado de opções de atendimentos elegíveis com nome do paciente e dados operacionais; verificar que atende enfermagem/gestão e admin sem expor registros já internados na seleção.

## 2. Cliente e validação

- [x] 2.1 Adicionar ao cliente Xano operações de leitos e internações, normalização de referências e tratamento de falhas sem limpar sessão; verificar testes do contrato HTTP.
- [x] 2.2 Implementar validadores de número, referências, status e datas de entrada/saída; verificar casos válidos, duplicados, datas inválidas e estados encerrados.

## 3. Estado e interface Reflex

- [x] 3.1 Adicionar ao `AuthState` estados e eventos explícitos para leitos, internações, criação e alta; verificar autorização e preservação da sessão em falhas.
- [x] 3.2 Criar interface protegida para cadastro/listagem de leitos, criação de internação com leitos livres e alta de internações ativas; verificar que recepcionista e médico não recebem controles ou dados.

## 4. Testes e validação final

- [x] 4.1 Adicionar testes de autorização, validadores, cliente e `AuthState` cobrindo duplicidade, leito ocupado, atendimento repetido, alta e papéis bloqueados; verificar a suíte completa.
- [x] 4.2 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate cadastro-internacoes-leitos --strict`; confirmar todos os comandos sem erro.
- [x] 4.3 Realizar validação manual com enfermagem/gestão, admin, recepcionista e médico no ambiente live; confirmar seleção de atendimento, cadastro, ocupação, alta, liberação, bloqueios e ausência de dados parciais antes do archive.
