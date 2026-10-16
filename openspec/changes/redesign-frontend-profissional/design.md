# Design

## Context

Todas as páginas são funções Reflex ligadas ao `AuthState`. Cada módulo repete
a mesma estrutura (coluna centralizada, título, botão "Voltar", cartões) e usa
`rx.text(color="red"/"green")` para mensagens. O tema do Radix nunca foi
configurado: `rx.App` é criado sem `theme`, portanto vale o padrão (accent azul,
cinza neutro, raio médio). Os testes existentes (88) cobrem validações,
autorização, cliente Xano e eventos do `AuthState`, e não dependem da camada
visual.

## Goals / Non-Goals

**Goals:**

- Identidade visual única, aplicada por tema e tokens, sem hex solto nas páginas.
- Navegação persistente e consistente em todas as páginas internas.
- Feedback visível em toda ação (carregando, sucesso, erro, confirmação).
- Dados apresentados em tabelas, badges e linha do tempo.

**Non-Goals:**

- Alterar regras de negócio, validações, autorização ou o cliente Xano.
- Introduzir tecnologia de frontend fora do Reflex.

## Decisions

### `rx.theme` e não troca de biblioteca

O Radix Themes continua sendo a base. No Reflex 0.9 `rx.App(theme=...)` está
obsoleto: o tema é configurado uma vez em `RadixThemesPlugin(theme=tema_app())`
no `rxconfig.py`, com `accent_color="teal"`, `gray_color="slate"`,
`radius="medium"`, `scaling="100%"` e `panel_background="solid"`. O
`styles.css` sobrescreve a escala `--accent-*` com a paleta azul-petróleo
própria, a fonte (`--default-font-family`) e os tokens `--gh-*` (fundo, sombras,
barra lateral). Componentes herdam o visual sem receber cores individuais.
### Ícones: Lucide (SVG) e SVG próprio apenas para marca

`rx.icon` renderiza ícones Lucide como SVG inline, já instalados com o Reflex.
SVG escrito à mão fica restrito à marca e às ilustrações de estado vazio/login
(`rx.html` com markup estático e confiável).

### Feedback sem reescrever os eventos de negócio

Os eventos existentes já preenchem `erro_*`/`sucesso_*`. Em vez de alterar cada
um, a UI encadeia eventos: `iniciar_acao(chave)` → evento original →
`notificar_resultado(dominio)` → `encerrar_acao`. Cada evento do Reflex é
processado em ordem e seu delta é enviado ao navegador ao terminar, então o
indicador de carregamento aparece enquanto o evento de negócio aguarda o Xano.
`notificar_resultado` valida o domínio em uma lista fixa (o argumento vem do
cliente), dispara `rx.toast` e limpa apenas a mensagem de sucesso; o erro
permanece visível junto ao formulário.

### Busca por tabela

Um único termo de busca no estado, zerado ao entrar em cada página, e variáveis
computadas `*_filtradas` que comparam o termo (sem acento/caixa) com os valores
do registro. Nenhuma consulta extra ao Xano.

### Indicadores do dashboard

O painel guarda só totais (`painel_*`), nunca listas de pacientes. Pacientes,
médicos e atendimentos são contados pelo total da paginação do Xano
(`itemsTotal`, via `page=1&per_page=1`), com fallback para a lista completa
quando o endpoint não é paginado. Leitos e internações são listas pequenas,
usadas apenas para contar status. As consultas dos recursos permitidos ao papel
rodam em paralelo (`ThreadPoolExecutor`), então o custo é o da consulta mais
lenta e não a soma. A leitura é reaproveitada por 60 s (`VALIDADE_PAINEL_SEGUNDOS`);
Atualizar força nova leitura e Limpar invalida a anterior. Falha parcial mantém
os demais indicadores, mostra aviso (inline e, em Atualizar, toast de erro) e falha
total não marca a leitura como recente. Sem dado, o card mostra "—".
### Item ativo estático e fonte única da navegação

O item ativo do menu não depende do estado do servidor (`router.page.path` só
atualizava depois da fila de eventos, bloqueada pelas chamadas ao Xano da página
nova). Cada página informa a própria rota a `pagina(...)`, e o item ativo sai
pronto no primeiro desenho. `NAVEGACAO` (em `ui/layout.py`) é a fonte única de
rótulo, rota, ícone, permissão e descrição, usada pelo menu e pelos atalhos do
painel.

### Carregamento de página

As rotas usam `ao_carregar(...)`: `iniciar_acao("carregando")` → carregador →
`encerrar_acao`. Enquanto `carregando_pagina` ou o estado ainda não foi
hidratado, tabelas e indicadores mostram esqueleto, a leitura anterior (se
houver) continua visível com o aviso "Atualizando" e os botões de ação ficam
bloqueados (inclusive antes da hidratação, para não perder cliques).

### Atualizar e Limpar

`Atualizar` reutiliza o carregador da própria página com carregamento e toast de
resultado (`notificar_atualizacao`); no histórico, `atualizar_historico`
recarrega os pacientes e refaz a consulta do selecionado. `Limpar` chama
`limpar_tela(tela)`, que só aceita telas de `CAMPOS_LIMPEZA` (lista fixa de
campos, pois o argumento vem do cliente) e zera leitura, seleção, busca,
formulário e mensagens. Listas de referência de outra tela (ex.: pacientes do
formulário de atendimentos) são recarregadas ao entrar na tela.

### Paginação de pacientes e médicos

O Xano pagina `/patients` e `/doctors` (25 por página; `itemsTotal` no payload).
`listar_*_pagina` devolve registros e total; sem total (endpoint não paginado) a
lista conta como uma página. `mudar_pagina(tela, delta)` aceita só essas duas
telas, limita a página ao intervalo válido, zera a busca e recarrega; se a página
atual esvaziar, volta à primeira. A busca continua local e vale só para a página
exibida (a interface avisa). O formulário de atendimentos não depende da página
exibida: usa listas de referência (`pacientes_referencia`, `medicos_referencia`,
somente id e nome) obtidas por `listar_todos_*`, que percorre as páginas com
limite de segurança (2000 registros) e detecta endpoints que ignoram a
paginação. A checagem de CRM duplicado também passou a olhar todas as páginas.

### Layout responsivo

Barra lateral fixa em telas largas; em telas estreitas ela é substituída por
barra superior com gaveta (`rx.drawer`) contendo a mesma navegação. A navegação
usa as mesmas variáveis `pode_ver_*` e as mesmas rotas atuais.

## Risks / Trade-offs

- **[Risco]** Fonte indisponível. **Mitigação:** a Inter é servida pelo próprio app
  (`assets/fonts/`, licença OFL incluída), com a fonte do sistema como fallback.
- **[Risco]** Encadeamento esconder falha de evento. **Mitigação:**
  `encerrar_acao` é evento independente e sempre executa.
- **[Risco]** Reescrita visual ocultar acesso autorizado. **Mitigação:** a
  navegação reutiliza as mesmas condições; teste compara a matriz por papel.

## Migration Plan

1. Fundação (tema, tokens, ícones, componentes).
2. Layout compartilhado e navegação.
3. Feedback de ações.
4. Telas (tabelas, linha do tempo, dashboard, login).
5. Executar testes, `reflex compile` e validação visual.
