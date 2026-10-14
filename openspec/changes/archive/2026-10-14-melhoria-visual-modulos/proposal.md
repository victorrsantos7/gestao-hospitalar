# Proposal

## Why

As telas internas já possuem os fluxos funcionais necessários, mas ainda usam
composições básicas e pouco consistentes com o novo login/dashboard. A próxima
melhoria deve levar a mesma linguagem visual para os módulos operacionais sem
alterar seu comportamento.

## What Changes

- Reformular visualmente Pacientes, Médicos, Convênios, Atendimentos, Internações/Leitos, Histórico e Transferências.
- Padronizar cabeçalhos, espaçamentos, painéis, listas, formulários, mensagens e ações.
- Reutilizar a identidade azul-marinho, azul hospitalar, branco e cinzas claros.
- Preservar textos atuais, eventos, rotas, permissões, validações, endpoints e State.
- Manter responsividade para desktop e mobile.

Fora do escopo: novas consultas, novos indicadores, alteração de autorização,
alteração de dados, mudança de fluxo ou criação de funcionalidades.

## Capabilities

Nenhuma. Esta change altera somente apresentação visual e não modifica requisitos funcionais.

## Impact

- Componentes Reflex das telas operacionais.
- Nenhuma alteração em Xano, cliente HTTP ou regras de negócio.
- Testes funcionais existentes devem continuar passando sem mudança de comportamento.
