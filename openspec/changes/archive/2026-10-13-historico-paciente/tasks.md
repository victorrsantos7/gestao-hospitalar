# Tasks

## 1. Persistência e API Xano

- [x] 1.1 Criar endpoint privado de histórico por paciente com composição de atendimentos, diagnósticos, internações e transferências; verificar autorização, campos e ordenação no ambiente live.

## 2. Cliente e normalização

- [x] 2.1 Adicionar ao cliente Xano consulta de histórico e normalização dos eventos; verificar contrato HTTP e ausência de dados privados.
- [x] 2.2 Implementar validadores e ordenação de eventos; verificar paciente inexistente, histórico vazio e datas iguais.

## 3. Estado e interface Reflex

- [x] 3.1 Adicionar ao `AuthState` seleção de paciente, carregamento, eventos e mensagens de histórico; verificar autorização e falhas sem dados parciais.
- [x] 3.2 Criar rota `/historico`, acesso no dashboard e linha do tempo somente leitura; verificar seleção sem digitação manual de ID.

## 4. Testes e validação final

- [x] 4.1 Adicionar testes de autorização, cliente, normalização, ordenação, histórico vazio e falhas; verificar a suíte completa.
- [x] 4.2 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate historico-paciente --strict`.
- [x] 4.3 Realizar validação manual por enfermagem/gestão, admin, recepcionista e médico antes do archive.
