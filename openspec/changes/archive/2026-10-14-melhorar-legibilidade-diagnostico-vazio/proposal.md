# Proposal

## Why

A mensagem exibida quando um atendimento não possui diagnósticos está com
contraste insuficiente sobre o fundo claro, dificultando sua leitura durante a
consulta clínica.

## What Changes

- Aplicar uma cor leve, porém legível, à mensagem "Nenhum diagnóstico encontrado.".
- Preservar o fluxo, as permissões e os demais elementos da tela de Diagnósticos.
- Fora do escopo: alterar formulário, navegação, regras de negócio ou persistência.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `cadastro-diagnosticos`: garantir legibilidade do estado vazio na consulta de diagnósticos.

## Impact

- Componente de Diagnósticos dentro da tela de Atendimentos.
- Sem alterações em API, banco de dados, permissões ou dependências.
