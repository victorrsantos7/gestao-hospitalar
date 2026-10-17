# Design

## Decisions

### Conteúdo estático, visibilidade por permissão

O conteúdo vive em `TOPICOS` (dataclass `Topico`), sem Reflex, e a interface o
percorre em Python na compilação: um botão e um bloco por tópico, ambos
envolvidos em `rx.cond` com a variável `pode_ver_*` do `AuthState` e, no bloco,
com `ajuda_topico == id`. Evita `rx.foreach` sobre estruturas aninhadas e
permite ícone SVG estático por tópico (ícone dinâmico carregaria todo o Lucide).

### Modal embutido

`rx.dialog.root` controlado por `ajuda_aberta` (`on_open_change`), aberto pelo
FAB; nada navega. Os itens do menu da ajuda são `<button>` nativos (teclado e
leitor de tela). `selecionar_ajuda` ignora ids desconhecidos. O estado é
reiniciado no logout.

### Estilo

FAB fixo de 48 px na cor petróleo (canto inferior direito), modal de até 820 px
com duas colunas (210 px + conteúdo) e altura limitada ao viewport, com rolagem
independente. Abaixo de 640 px o menu vira uma faixa horizontal.

## Risks

- O texto precisa acompanhar o produto: os testes cobrem módulos do menu,
  permissões e tipos de convênio, mas não o conteúdo dos passos.
