# Design

## Context

O projeto já possui cliente HTTP para Xano, matriz fixa de autorização e
fluxos de pacientes e médicos implementados em `AuthState`. A nova entidade
deve seguir esses limites e manter a interface Reflex existente. Ver
`proposal.md` para a motivação e a especificação delta para o contrato
observável.

## Goals / Non-Goals

**Goals:**

- Expor operações autenticadas de listar, consultar, criar, atualizar e
  excluir convênios.
- Centralizar validação e mensagens do fluxo no estado Reflex, sem confiar
  apenas na interface.
- Aplicar a permissão `convenios` tanto na rota quanto nos eventos do estado.
- Entregar uma tela funcional coerente com as telas atuais.

**Non-Goals:**

- Vincular convênios a atendimentos nesta change.
- Implementar faturamento, cobertura calculada ou regras de autorização de
  procedimentos.
- Fazer o redesenho visual global do sistema.

## Decisions

- **Reutilizar `AuthState` e `XanoClient`:** mantém autenticação, tratamento de
  erros, limpeza de sessão e logging no padrão já validado. Um novo estado ou
  cliente separado duplicaria regras sensíveis.
- **Usar nome normalizado como identificador lógico único:** evita duplicidade
  causada por diferenças de maiúsculas, espaços ou acentos; o Xano continuará
  sendo a autoridade final da unicidade.
- **Representar tipo como conjunto fechado:** a UI usará seleção controlada e
  o estado/endpoint validarão novamente os valores, evitando tipos arbitrários.
- **Separar componentes da tela em formulário, linha e detalhe:** segue o
  padrão de `medicos.py` e permite incluir manutenção sem alterar a estrutura
  das demais telas.
- **Manter preconditions no Xano:** a autorização no Reflex melhora a
  experiência e protege a rota, enquanto a API permanece protegida contra
  chamadas diretas.

## Risks / Trade-offs

- [Risco] Exclusão pode conflitar com futuros atendimentos vinculados.
  Mitigação: o endpoint deve rejeitar exclusão com dependências; a tela exibe
  erro genérico e a regra poderá ser refinada na change de atendimentos.
- [Risco] A validação preventiva de duplicidade pode sofrer concorrência.
  Mitigação: manter índice único no Xano e tratar resposta de conflito.
- [Risco] Os endpoints ainda precisam ser publicados no ambiente live do Xano.
  Mitigação: validar manualmente cada operação autenticada antes do archive.

## Migration Plan

1. Criar a tabela `convenios` no Xano com índice único para o nome
   normalizado e endpoints privados.
2. Implementar cliente, estado, tela, rota e acesso no dashboard.
3. Executar testes, compilação Reflex e validação manual com papéis permitidos
   e negados.
4. Em caso de falha, retirar o acesso da navegação e corrigir os endpoints sem
   alterar os dados existentes de pacientes ou médicos.
