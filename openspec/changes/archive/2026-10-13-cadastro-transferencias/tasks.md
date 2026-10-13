# Tasks

## 1. Persistência e API Xano

- [x] 1.1 Criar a tabela `transferencias` com internação, data, destino, motivo e índice de internação; verificar schema no Xano.
- [x] 1.2 Criar endpoints privados de criação e listagem por internação, com preconditions de enfermagem/gestão ou admin e bloqueio de internação encerrada; verificar no ambiente live.

## 2. Cliente e validação

- [x] 2.1 Adicionar ao cliente Xano criação e listagem de transferências com tratamento de falhas; verificar contrato HTTP.
- [x] 2.2 Implementar validadores de referência, data, destino e motivo; verificar casos vazios, inválidos e válidos.

## 3. Estado e interface Reflex

- [x] 3.1 Adicionar ao `AuthState` estado, carregamento, criação e mensagens de transferências; verificar autorização e sessão em falhas.
- [x] 3.2 Integrar histórico e formulário à tela de internações, ocultando criação para internações encerradas; verificar múltiplos registros em ordem de data.

## 4. Testes e validação final

- [x] 4.1 Adicionar testes de autorização, validadores, cliente e `AuthState` para internação ativa/encerrada, múltiplas transferências e papéis negados; verificar a suíte completa.
- [x] 4.2 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate cadastro-transferencias --strict`.
- [x] 4.3 Realizar validação manual por enfermagem/gestão, admin, recepcionista e médico antes do archive.
