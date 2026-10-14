# Design

## Context

A aplicação possui módulos funcionais concluídos e textos visíveis espalhados
por componentes Reflex, `AuthState` e testes. A revisão deve atuar somente nas
strings destinadas ao usuário, sem renomear símbolos ou contratos técnicos.

## Goals / Non-Goals

**Goals:**

- Corrigir português brasileiro nos textos visíveis.
- Padronizar acentos, capitalização e termos dos módulos.
- Manter mensagens coerentes entre telas e State.
- Atualizar asserções de testes quando a mensagem visível mudar.

**Non-Goals:**

- Alterar identificadores Python, nomes de campos Xano, endpoints ou logs técnicos.
- Alterar validações, autorizações, eventos ou fluxo de navegação.
- Traduzir documentação técnica ou scripts Xano nesta etapa.

## Decisions

### Separação entre texto visível e identificador técnico

Somente strings exibidas em componentes, mensagens de sucesso/erro e títulos
serão corrigidas. Variáveis como `erro_internacao`, recursos como
`RECURSO_INTERNACOES` e campos Xano permanecem inalterados para evitar regressões.

### Vocabulário

Usar português brasileiro consistente: `Médico`, `Convênio`, `Atendimento`,
`Internação`, `Leito`, `Transferência`, `Histórico`, `Diagnóstico`, `Descrição`,
`Código`, `Saída` e `Usuário`.

### Verificação

Pesquisar strings sem acento nos módulos de interface e State, revisar
manualmente cada ocorrência e executar a suíte completa, compilação Reflex e
validação OpenSpec. Nenhum teste funcional deve mudar de comportamento; apenas
asserções de texto podem ser atualizadas.

## Risks / Trade-offs

- **[Risco]** Uma string técnica pode ser alterada por engano.
  **Mitigação:** limitar mudanças a textos visíveis e revisar o diff antes do commit.
- **[Risco]** Testes podem depender de mensagens antigas.
  **Mitigação:** atualizar somente as expectativas correspondentes às mensagens exibidas.

## Migration Plan

1. Levantar textos visíveis sem acentuação.
2. Corrigir componentes e mensagens do State.
3. Atualizar testes de mensagens.
4. Executar validações automáticas e revisar diff.
5. Arquivar e publicar a change sem alterar contratos técnicos.

## Open Questions

Nenhuma.
