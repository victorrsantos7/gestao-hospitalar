# Design

## Context

A persistencia principal do projeto esta no Xano e o login já retorna o papel
na sessão Reflex. Ainda não existem entidades da jornada do paciente no Xano ou
na aplicação.

## Goals / Non-Goals

**Goals:**

- Criar o primeiro recurso de domínio no Xano e consumi-lo pelo backend Reflex.
- Garantir CPF válido e único antes da gravação.
- Separar listagem resumida de consulta detalhada para reduzir exposição de
  dados pessoais.
- Usar autorização fixa antes de executar cada operação.

**Non-Goals:**

- Atualizar ou excluir pacientes.
- Criar relacionamentos com atendimento, médico ou convênio nesta change.
- Criar histórico clínico, internação ou transferência.

## Decisions

1. **Tabela Xano `pacientes`.**
   A tabela terá `id`, `nome`, `cpf`, `data_nascimento`, `telefone`, `endereco`
   e `contato_emergencia`, com índice único para CPF normalizado. O CPF será
   armazenado somente com dígitos para comparação consistente.

2. **APIs separadas por operação.**
   Usar endpoints distintos para listar, consultar por identificador e criar.
   Cada endpoint terá validação de papel no fluxo do backend antes da chamada
   remota; a API não será tratada como autorização exclusiva da interface.

3. **Validação em duas camadas.**
   O estado Reflex fará validação imediata para feedback, mas a API/backend
   repetirá validação de campos, CPF e duplicidade. A validação no cliente não
   será considerada controle de segurança.

4. **Listagem sem contato de emergência.**
   A resposta de listagem conterá apenas identificador, nome, data de
   nascimento e telefone. O CPF completo e o contato de emergência ficarão
   restritos à consulta detalhada autorizada.

5. **CPF validado por algoritmo local e unicidade remota.**
   A validação dos dígitos verificadores será determinística e testável sem
   rede; a unicidade dependerá de índice e consulta no Xano para lidar com
   concorrência.

## Risks / Trade-offs

- **[CPF é dado sensível]** -> mascarar listagens, limitar acesso por papel e
  não registrar CPF completo em logs.
- **[Condição de corrida em CPFs]** -> manter índice único no Xano e tratar o
  erro de conflito como duplicidade.
- **[API pública exposta]** -> proteger o grupo de API com credencial de serviço
  antes de publicar dados reais; o backend Reflex continuará sendo a autoridade
  de papel.
- **[Campos de endereço variam]** -> iniciar com texto simples e evitar
  modelagem de endereço externo nesta primeira fatia.

## Migration Plan

1. Criar a tabela e endpoints no Xano em ambiente de teste.
2. Implementar validador de CPF, cliente e testes unitários.
3. Implementar operações de criação/listagem/detalhe com autorização.
4. Criar estado e tela Reflex, validar mensagens e campos sensíveis.
5. Testar com recepcionista, médico, admin e tentativa negada.
6. Rollback: remover a rota/tela da aplicação e preservar a tabela remota sem
   apagar registros criados durante os testes.
