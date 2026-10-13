# Design

## Context

A aplicação já possui atendimentos e diagnósticos persistidos no Xano, além de
uma matriz de autorização que reserva `internacoes` e `leitos` para
enfermagem/gestão e admin. O atendimento é a origem da internação e um paciente
pode acumular internações ao longo do tempo, mas cada atendimento pode gerar no
máximo uma internação.

## Goals / Non-Goals

**Goals:**

- Criar tabelas e endpoints protegidos para leitos e internações.
- Manter o status do leito coerente com a existência de internação ativa.
- Implementar criação e alta como operações de domínio, sem edição arbitrária.
- Exibir referências úteis de paciente, atendimento e leito na interface.
- Validar autorização e regras de ocupação no backend e no State Reflex.

**Non-Goals:**

- Transferências entre áreas, que serão uma change posterior.
- Histórico consolidado, relatórios e gestão de tipos de leito.
- Edição ou exclusão de leitos e internações.
- Reserva antecipada de leito sem internação.

## Decisions

### Modelo de dados

Criar a tabela `leitos` com `id`, `numero` único e `status` controlado pelos
fluxos de internação (`livre`/`ocupado`). Criar a tabela `internacoes` com
`id`, `atendimento_id`, `paciente_id`, `leito_id`, `data_entrada`,
`data_saida` opcional, `status` (`internado`/`alta`) e `created_at` privado.

A duplicação de `paciente_id` na internação será validada contra o paciente do
atendimento e facilita consultas operacionais sem expor a equipe à cadeia
completa de joins. O número do leito terá índice único.

### Operações protegidas

Adicionar endpoints privados para cadastrar/listar leitos, listar internações,
criar internação e registrar alta. Todos consultarão `usuarios_hospital` e
permitirão somente `enfermagem_gestao` e `admin`.

O cadastro de leito não aceitará `status` de entrada. A criação de internação
buscará o atendimento, rejeitará atendimento que já possua qualquer internação,
buscará leito livre, criará a internação e marcará o leito como ocupado no mesmo
fluxo protegido.
A alta verificará status `internado`, validará a data, atualizará a internação e
liberará o leito associado.

### Exclusividade e consistência

As regras de ocupação serão aplicadas no backend, nunca apenas na interface.
As operações de criação e alta deverão usar a unidade transacional disponível
no Xano para que a criação da internação e a atualização do leito sejam uma
operação única. Se a atualização de qualquer lado falhar, nenhuma alteração
parcial deverá permanecer.

O cliente não enviará status de leito nem status de internação para criação;
esses valores serão definidos pelo endpoint. A interface exibirá ações de alta
somente para internações ativas.

### Integração com Reflex

Adicionar ao `AuthState` estados separados para leitos e internações, eventos
explícitos para número, referências, data de entrada e data de saída, além de
mensagens genéricas de erro. A tela poderá ter seções de leitos e internações,
com seleção de atendimento elegível e leito livre no formulário de internação e ação de alta no item
ativo.

Adicionar um endpoint operacional de opções de atendimento para
enfermagem/gestão e admin. Ele exibirá paciente, data, tipo e motivo, omitirá
atendimentos já vinculados a internações na lista apresentada e manterá o ID
somente como valor interno da opção selecionada. O backend continuará validando
o vínculo no momento da criação.

As rotas e componentes serão protegidos por `RECURSO_LEITOS` e
`RECURSO_INTERNACOES`; o backend continuará sendo a autoridade final.

### Validação e respostas

Validar número de leito, referências positivas, datas ISO, data de saída não
anterior à entrada e estados permitidos. Respostas de consulta conterão apenas
campos operacionais necessários, com nomes de paciente, atendimento e leito
quando disponíveis, sem token ou campos internos.

### Testes e publicação

Adicionar testes de validadores, autorização, cliente Xano e `AuthState`, com
ênfase em duplicidade, ocupação exclusiva, alta, falha transacional e papéis
negados. Publicar tabela e endpoints no Xano live, executar a suíte completa,
`reflex compile --dry`, validação OpenSpec e testes manuais por papel antes do
archive.

## Risks / Trade-offs

- **[Risco]** Duas criações concorrentes podem disputar o mesmo leito.
  **Mitigação:** agrupar verificação, criação e atualização em transação no
  backend e testar tentativas repetidas.
- **[Risco]** Dados legados podem conter status de leito divergente.
  **Mitigação:** a tabela será nova nesta change e o status será inicializado
  como `livre`; não haverá migração de ocupações antigas.
- **[Risco]** Uma alta duplicada pode liberar um leito já reutilizado.
  **Mitigação:** exigir status `internado` antes da alta e atualizar por
  identificador da internação ativa.
- **[Risco]** Consultas com referências relacionadas podem expor dados além do
  necessário.
  **Mitigação:** limitar os campos de resposta a dados operacionais e manter
  endpoints privados.

## Migration Plan

1. Criar tabelas, índices e endpoints protegidos no Xano.
2. Publicar no ambiente live e testar as preconditions de cada papel.
3. Implementar cliente, validadores, State e interface Reflex.
4. Executar testes automáticos e confirmar manualmente cadastro, internação,
   alta, ocupação exclusiva e bloqueios.
5. Em caso de falha, remover apenas os recursos novos ou desativar as rotas sem
   alterar pacientes, atendimentos ou diagnósticos existentes.

## Open Questions

Nenhuma. O número do leito é o identificador operacional inicial e seu status
será derivado exclusivamente dos fluxos de internação.
