# Design

## Context

A aplicação já possui internações protegidas por papel, com leito, entrada,
saída e status. A matriz reserva `transferencias` para enfermagem/gestão e
admin. Esta change registra o movimento entre setores como histórico próprio,
sem alterar a ocupação física do leito.

## Goals / Non-Goals

**Goals:**

- Criar tabela e endpoints privados para transferências.
- Validar internação ativa, data, destino e motivo no backend.
- Exibir o histórico dentro da tela de internações.
- Permitir múltiplos registros ordenados por data.
- Manter autorização e mensagens de falha consistentes com os módulos existentes.

**Non-Goals:**

- Trocar automaticamente o leito da internação.
- Editar ou excluir transferências.
- Criar setores cadastráveis ou uma tabela de unidades nesta etapa.
- Consolidar o histórico completo do paciente.

## Decisions

### Modelo de dados

Criar a tabela `transferencias` com `id`, `internacao_id`, `data_transferencia`,
`destino`, `motivo` e `created_at` privado. A referência à internação será
obrigatória e o destino será texto controlado por validação de não vazio nesta
primeira versão.

A alternativa de criar uma tabela de setores foi deixada para uma change futura,
pois o domínio ainda não define catálogo, código ou hierarquia de áreas.

### Endpoints protegidos

Adicionar endpoints privados para criar transferência e listar transferências
por internação. Ambos consultarão `usuarios_hospital` e aceitarão somente
`enfermagem_gestao` e `admin`.

A criação buscará a internação e exigirá status `internado`. A listagem filtrará
por `internacao_id` e ordenará por `data_transferencia` crescente. Nenhum
endpoint atualizará leitos ou a própria internação.

### State e interface

Adicionar estado para formulário e histórico de transferências ao `AuthState`.
A tela de internações exibirá uma seção por internação ativa/autorizada com
formulário de destino, motivo e data, além dos registros anteriores. A
internação encerrada exibirá apenas o histórico, sem ação de criação.

### Validação e respostas

Validar referência positiva, data ISO, destino e motivo não vazios. Respostas
conterão somente identificador, internação, data, destino e motivo, sem tokens ou
campos internos.

### Testes e publicação

Adicionar testes de validadores, cliente Xano, autorização e `AuthState` para
internação ativa, múltiplas transferências, internação encerrada, histórico
ordenado e papéis negados. Publicar no Xano live, executar suíte, compilação,
OpenSpec e validação manual antes do archive.

## Risks / Trade-offs

- **[Risco]** Destinos textuais podem variar na grafia.
  **Mitigação:** manter texto obrigatório agora e deixar catálogo de setores para
  uma mudança específica.
- **[Risco]** Uma transferência pode ser registrada com data anterior a outra.
  **Mitigação:** ordenar o histórico por data e preservar o registro; validação
  de sequência temporal pode ser adicionada quando houver regra formal.
- **[Risco]** Usuários podem esperar que a transferência altere o leito.
  **Mitigação:** deixar essa decisão explícita na interface e manter a operação
  fora do escopo desta change.

## Migration Plan

1. Criar tabela e endpoints protegidos no Xano.
2. Implementar cliente, validadores, State e histórico na tela de internações.
3. Executar testes automáticos e validar papéis no ambiente live.
4. Confirmar manualmente criação, consulta, bloqueio e múltiplas transferências.
5. Em caso de falha, remover apenas os recursos novos sem alterar internações ou leitos.

## Open Questions

Nenhuma. O destino permanece textual nesta etapa e a transferência não altera o leito.
