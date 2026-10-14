# Proposal

## Why

A interface ainda possui vários textos sem acentuação, como `Internacoes`,
`Convenios` e `Historico`. Isso reduz a qualidade percebida do sistema e deixa a
comunicação inconsistente com o português brasileiro usado na documentação.

## What Changes

- Corrigir acentuação e capitalização dos textos visíveis da interface.
- Revisar títulos, botões, placeholders, mensagens de erro e mensagens de sucesso.
- Preservar nomes técnicos de funções, variáveis, endpoints, recursos e campos de API.
- Preservar comportamento, rotas, permissões, eventos e contratos do sistema.
- Atualizar testes que verificam mensagens exibidas ao usuário.

Fora do escopo: alteração de regras de negócio, dados persistidos, nomes de
colunas Xano, endpoints, logs técnicos e identificadores internos.

## Capabilities

Nenhuma. Esta change altera somente conteúdo textual visível e não modifica requisitos funcionais.

## Impact

- Textos visíveis nos componentes Reflex e mensagens do `AuthState`.
- Testes unitários que comparam mensagens exibidas.
- Nenhuma alteração em Xano ou na lógica de autenticação/autorização.
