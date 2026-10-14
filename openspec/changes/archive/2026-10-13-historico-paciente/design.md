# Design

## Context

O projeto já possui tabelas e endpoints protegidos para pacientes, atendimentos,
diagnósticos, internações e transferências. A matriz fixa reserva o recurso
`historico` para enfermagem/gestão e admin. O histórico deve reutilizar esses
dados sem alterar os módulos de origem.

## Goals / Non-Goals

**Goals:**

- Expor uma consulta consolidada protegida por papel.
- Permitir seleção de paciente por nome, sem digitação manual de ID.
- Unificar eventos em uma estrutura com tipo, data e campos operacionais.
- Ordenar a linha do tempo e tratar ausência de eventos.
- Manter a consulta somente leitura e sem duplicação de dados.

**Non-Goals:**

- Criar ou editar pacientes, atendimentos, diagnósticos, internações ou transferências.
- Criar uma tabela física duplicada de histórico.
- Implementar relatórios, filtros avançados ou exportação.
- Liberar histórico para recepcionista ou médico nesta etapa.

## Decisions

### Consulta consolidada

Adicionar endpoint privado de histórico por paciente, protegido por
`usuarios_hospital`. O endpoint buscará os registros relacionados nas tabelas
existentes e retornará uma lista de eventos normalizados com `tipo`, `data` e
campos operacionais. A consulta será feita no backend para evitar chamadas
separadas e inconsistência de ordenação no navegador.

A alternativa de montar a linha do tempo com uma chamada por módulo no cliente
foi descartada por aumentar latência, expor mais contratos e dificultar falhas
parciais coerentes.

### Seleção de paciente

A tela carregará opções de pacientes autorizadas e exibirá nome, data de
nascimento e identificador apenas como contexto. O valor interno será o ID, mas
o usuário não o digitará manualmente.

### Formato dos eventos

Cada evento terá tipo (`atendimento`, `diagnostico`, `internacao` ou
`transferencia`), data, título e detalhes operacionais. O endpoint não retornará
tokens, campos privados de autenticação ou dados sensíveis desnecessários.

### State e interface

Criar rota protegida `/historico`, acessível pelo dashboard para os papéis
permitidos. O `AuthState` manterá pacientes disponíveis, paciente selecionado,
eventos, mensagens e carregamento. A interface renderizará a linha do tempo em
ordem cronológica e estado vazio quando não houver eventos.

### Validação e falhas

Validar paciente positivo e existente no backend. Qualquer falha na composição
será convertida em erro genérico; não será exibida uma linha do tempo parcial
como se estivesse completa.

### Testes e publicação

Adicionar testes de contrato do cliente, normalização/ordenação, autorização,
seleção e falhas. Publicar o endpoint no Xano live, executar suíte, compilação,
OpenSpec e validação manual antes do archive.

## Risks / Trade-offs

- **[Risco]** Eventos de módulos diferentes podem ter campos e datas distintas.
  **Mitigação:** normalizar no endpoint para tipo, data, título e detalhes.
- **[Risco]** Uma falha em uma fonte pode interromper o histórico inteiro.
  **Mitigação:** retornar erro genérico e nenhum resultado parcial.
- **[Risco]** O histórico pode incluir dados sensíveis além do necessário.
  **Mitigação:** limitar campos no endpoint e manter autorização restrita.

## Migration Plan

1. Criar endpoint de histórico consolidado no Xano.
2. Implementar cliente, normalização, State, rota e linha do tempo.
3. Executar testes automáticos e validação manual por papel.
4. Em caso de falha, remover apenas o endpoint e a rota novos.

## Open Questions

Nenhuma. O histórico será somente leitura e usará as entidades existentes.
