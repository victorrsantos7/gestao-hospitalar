# Proposal

## Why

O sistema não traz instruções de uso. Quem entra pela primeira vez (recepção,
médico, enfermagem) precisa descobrir sozinho o fluxo de cada módulo, os botões
Atualizar e Limpar, as regras de CPF/CRM e o que fazer quando uma leitura falha.

## What Changes

- Botão flutuante (FAB) no painel que abre a ajuda em um modal, sem trocar de página.
- Modal com lista de módulos à esquerda e instruções à direita (como usar e dicas).
  Cada módulo só aparece para quem tem acesso a ele (mesma regra do menu); os
  tópicos "Primeiros passos", "Perfis e acessos" e "Problemas comuns" aparecem para todos.
- Conteúdo em `ajuda.py` (dados puros), validado por testes contra o menu, as
  permissões do `AuthState` e os tipos de convênio.
- Layout responsivo: em telas estreitas os módulos viram uma faixa rolável acima do texto.

Fora do escopo: busca dentro da ajuda, ajuda contextual em cada tela e vídeos.

## Capabilities

### Modified Capabilities

- `interface-usuario`: ajuda de uso em modal.

## Impact

- Novos `gestao_hospitalar/ajuda.py`, `ui/ajuda.py` e `tests/test_ajuda.py`.
- `AuthState` (`ajuda_aberta`, `ajuda_topico`, `abrir_ajuda`, `set_ajuda_aberta`,
  `selecionar_ajuda`; reiniciados no logout), `dashboard.py` e `assets/styles.css`.
