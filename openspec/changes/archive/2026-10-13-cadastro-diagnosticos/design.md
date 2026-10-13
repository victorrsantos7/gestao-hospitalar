# Design

## Context

A aplicação já usa Xano como persistência remota para pacientes, médicos,
convênios e atendimentos. O `AuthState` centraliza sessão, autorização,
carregamento de dados e eventos Reflex; a matriz fixa já declara o recurso
`diagnosticos` para médico e admin. O atendimento possui detalhe consultável,
que será o ponto natural para exibir os diagnósticos.

## Goals / Non-Goals

**Goals:**

- Criar uma tabela Xano de diagnósticos com referência obrigatória a atendimento.
- Expor operações protegidas de criação e consulta por atendimento.
- Aplicar autorização no backend Xano e novamente no cliente Reflex antes das chamadas.
- Integrar formulário e listagem ao detalhe de atendimento sem duplicar o fluxo de autenticação.
- Validar entrada localmente e manter validação equivalente no backend.

**Non-Goals:**

- Alterar o contrato ou os dados existentes de atendimentos.
- Implementar edição, exclusão, prescrição ou classificação automática de CID.
- Criar histórico consolidado do paciente.
- Introduzir nova tecnologia ou persistência local paralela ao Xano.

## Decisions

### Tabela e referências no Xano

Criar a tabela `diagnosticos` com identificador, `atendimento_id`, `descricao`,
`codigo_cid` opcional e `data_diagnostico`. A referência ao atendimento será validada
antes da escrita e também protegida por precondition no endpoint, evitando
registros órfãos.

A alternativa de armazenar o diagnóstico como texto dentro de `atendimentos`
foi descartada porque um atendimento pode possuir vários diagnósticos e a
separação mantém o relacionamento do modelo de domínio.

### Endpoints protegidos

Adicionar endpoints privados para criar um diagnóstico e listar diagnósticos
por atendimento. As preconditions consultarão `usuarios_hospital` e permitirão
somente `medico` e `admin`; a resposta de listagem conterá apenas identificador,
descrição, código CID e data. Falhas remotas serão convertidas pelo cliente em
mensagem genérica, preservando a sessão.

A consulta será filtrada por `atendimento_id` no endpoint, em vez de carregar
todos os diagnósticos e filtrar no navegador, para reduzir exposição de dados
clínicos.

### Integração com o State e a interface

Adicionar ao `AuthState` campos para formulário, diagnóstico selecionado/lista,
erros e sucesso, além de eventos explícitos para os inputs. O carregamento dos
diagnósticos ocorrerá ao consultar o detalhe de um atendimento autorizado; o
formulário aparecerá somente quando `pode_acessar_recurso(diagnosticos)` for
verdadeiro.

O detalhe de atendimento exibirá a listagem e, para médico/admin, o formulário
de criação. Recepcionista e enfermagem/gestão não receberão dados nem controles
na interface, mas a proteção principal continuará no backend.

### Validação

Criar validadores puros para referência positiva, descrição não vazia e data ISO.
O código CID será opcional; quando informado, será aceito apenas se não estiver
vazio após a remoção de espaços. O cliente executará essas validações antes da
chamada Xano, enquanto os endpoints repetirão as regras para impedir bypass por
chamadas diretas.

### Verificação e publicação

Adicionar testes unitários dos validadores, autorização e contrato do cliente
Xano, além de testes do `AuthState` para sucesso, falhas, sessão preservada e
papéis negados. Validar com a suíte existente, `reflex compile --dry` e
validação OpenSpec antes da publicação.

## Risks / Trade-offs

- **[Risco]** O formato de código CID pode variar entre especialidades ou estar
  ausente em um diagnóstico inicial. **Mitigação:** aceitar CID opcional e, quando
  informado, armazenar apenas texto não vazio, deixando normalização fora do escopo.
- **[Risco]** Um endpoint mal configurado pode expor diagnósticos a outro papel.
  **Mitigação:** usar preconditions de papel no Xano, autorização no `AuthState`
  e testes explícitos para cada papel não autorizado.
- **[Risco]** A listagem do detalhe pode falhar depois de o atendimento carregar.
  **Mitigação:** manter o detalhe disponível, mostrar falha genérica de
  diagnósticos e não renderizar dados parciais.
- **[Risco]** A publicação Xano pode divergir entre draft e live.
  **Mitigação:** testar os endpoints publicados no ambiente live antes do
  archive e registrar a validação manual.

## Migration Plan

1. Criar tabela, índice ou referência necessária e endpoints privados no Xano.
2. Publicar os endpoints no ambiente live e testar autorização, criação e consulta.
3. Implementar cliente, validadores, `AuthState`, interface e testes.
4. Executar validações automáticas e confirmar manualmente os fluxos por papel.
5. Em caso de falha, remover os endpoints/tabela novos ou desativar a rota da
   interface; não alterar dados existentes de atendimentos.

## Open Questions

Nenhuma. As decisões pendentes não alteram o contrato desta change e podem ser
tratadas como detalhes de configuração durante a implementação.
