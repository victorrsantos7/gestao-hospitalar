# Tasks

## 1. Backend remoto

- [x] 1.1 Criar a tabela `atendimentos` no Xano com IDs de paciente, medico e convenio opcional, data, motivo e tipo; verificar a estrutura pela Meta API.
- [x] 1.2 Publicar endpoints privados de criacao, listagem e consulta detalhada com preconditions de autenticacao e papel; verificar respostas de sucesso, validacao e proibicao no ambiente live.

## 2. Cliente e validacao

- [x] 2.1 Adicionar ao cliente Xano os metodos de criacao, listagem e consulta de atendimentos; verificar headers, paths, payloads e tratamento de erros com testes de transporte.
- [x] 2.2 Criar validadores para data, motivo, tipo e IDs de referencias; verificar tipos permitidos, obrigatorios e rejeicao de entradas invalidas.

## 3. Estado e interface Reflex

- [x] 3.1 Adicionar ao `AuthState` os campos, setters, carregamento de referencias, cadastro e listagem de atendimentos; verificar autorizacao local, limpeza no logout e mensagens sem dados sensiveis.
- [x] 3.2 Criar a tela protegida `/atendimentos` com selecao de paciente, medico e convenio opcional, formulario e listagem; verificar acesso por papel e exibicao de falhas remotas.
- [x] 3.3 Integrar a rota e a navegacao do dashboard respeitando `RECURSO_ATENDIMENTOS`; verificar redirecionamento de sessao ausente ou papel sem permissao.

## 4. Testes e validacao

- [x] 4.1 Adicionar testes unitarios para validadores, cliente, autorizacao e `AuthState`; verificar cadastro valido, duplicidade/referencias invalidas, falha remota e papeis permitidos/negados.
- [x] 4.2 Executar a suite automatizada e `reflex compile --dry`; verificar que todos os testes e a compilacao passam.
- [x] 4.3 Executar `cmd /d /c openspec validate cadastro-atendimentos --strict`; verificar que a change esta valida.
- [x] 4.4 Realizar validacao manual na UI com recepcionista, medico, enfermagem/gestao e admin; registrar confirmacao explicita antes do archive.