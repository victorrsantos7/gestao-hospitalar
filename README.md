# Sistema de Gestão Hospitalar

Aplicação full-stack em [Reflex](https://reflex.dev) para gerenciar a jornada
do paciente dentro do hospital: cadastro de pacientes, médicos e convênios,
atendimentos, diagnósticos, internações, leitos e transferências.

## Documentação do projeto

- [AGENTS.md](AGENTS.md) — instruções para agentes de IA que trabalham neste projeto.
- [docs/project-overview.md](docs/project-overview.md) — visão geral do sistema.
- [docs/domain-model.md](docs/domain-model.md) — conceitos e relacionamentos do domínio.
- [openspec/config.yaml](openspec/config.yaml) — contexto e regras dos workflows do OpenSpec.
- [openspec/specs/](openspec/specs) — comportamento consolidado do sistema.
- [openspec/changes/](openspec/changes) — mudanças em andamento e histórico.

## Ambiente de desenvolvimento

Pré-requisitos: Python 3.10+.

```bash
py -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
reflex run
```

A aplicação fica disponível em `http://localhost:3000` (backend em `:8000`).

### Configuração do Xano

Use `.env.example` como referência e configure as variáveis no ambiente antes
de iniciar a aplicação. O `iniciar_reflex.bat` já define a URL pública de
desenvolvimento por padrão. A URL atual do grupo de API hospitalar é:

```text
https://x8ki-letl-twmt.n7.xano.io/api:3lVm5Wbj
```

Variáveis utilizadas:

- `XANO_API_URL` — obrigatória.
- `XANO_API_TOKEN` — opcional, somente para grupos protegidos.
- `XANO_TIMEOUT_SECONDS` — opcional; padrão de 10 segundos.
- `XANO_MAX_TENTATIVAS` — opcional; tentativas por leitura (1 a 5, padrão 3) em caso de limite de requisições (429), indisponibilidade ou falha de conexão. Escritas nunca são repetidas.
- `XANO_LIMITE_REQUISICOES` e `XANO_JANELA_SEGUNDOS` — opcionais; máximo de requisições por janela (padrão 8 a cada 20 s), abaixo do limite do plano do Xano, para o app esperar a vez em vez de receber 429. `XANO_LIMITE_REQUISICOES=0` desliga o controle.

### Logs de comunicação

O backend registra a comunicação entre eventos Reflex e o Xano em
`logs/gestao_hospitalar.log`. O log inclui evento, método, rota, status, duração
e quantidade de registros retornados, mas não grava senha, token ou payload de
pacientes. A BAT define `GESTAO_LOG_FILE` e `GESTAO_LOG_LEVEL`; para aumentar o
detalhamento, use `GESTAO_LOG_LEVEL=DEBUG` antes de iniciar.

O login usa o endpoint `POST /auth/login` do Xano e a tabela
`usuarios_hospital`. Crie usuários de teste diretamente no Xano; senhas não
devem ser armazenadas no repositório.

### Autorização por papel

As permissões são fixas no backend e negadas por padrão:

- `recepcionista`: pacientes, médicos, convênios e atendimentos.
- `medico`: pacientes, atendimentos e diagnósticos.
- `enfermagem_gestao`: internações, leitos, transferências e histórico.
- `admin`: todas as funcionalidades e gerenciamento de usuários.

Toda nova funcionalidade deve declarar seu recurso e validar o papel no
backend; ocultar um item da interface não substitui essa validação.

### Cadastro de pacientes

A rota `/pacientes` permite que recepcionista e admin cadastrem pacientes, e
que recepcionista, médico e admin consultem pacientes. O cadastro valida CPF
antes de enviar os dados ao Xano; a listagem resumida não retorna CPF nem
contato de emergência. Esses dados aparecem somente na consulta detalhada
autorizada.

O formulário aplica máscara e normalização ao CPF, telefone e contato de
emergência. Telefones seguem o padrão brasileiro de 10 ou 11 dígitos; nomes
aceitam letras, acentos, espaços, hífen e apóstrofo; e a data de nascimento
deve ser válida e não futura.

Os resultados da validação operacional estão em
[docs/validacao-cadastro-pacientes.md](docs/validacao-cadastro-pacientes.md).

## Interface

O visual é definido em três camadas, todas em Reflex:

- `rxconfig.py` configura o tema Radix (`RadixThemesPlugin(theme=tema_app())`).
- `assets/styles.css` guarda os tokens (`--gh-*`), a escala de cor petróleo e as
  classes `gh-*`. A fonte Inter (SIL OFL) é hospedada em `assets/fonts/` e declarada no
  próprio CSS, sem dependência de rede externa.
- `gestao_hospitalar/ui/` reúne marca/SVG (`icones.py`), componentes de
  formulário, tabela e feedback (`componentes.py`) e o layout com menu lateral
  (`layout.py`). `NAVEGACAO` é a fonte única dos módulos do menu e dos atalhos
  do painel.

Convenções para novas telas:

- Montar a página com `pagina(titulo, descricao, icone, rota, acoes, ...)`; a
  rota define o item ativo do menu.
- Usar `botao_acao`/`botao_icone` (carregamento, bloqueio de duplo clique e toast)
  e `confirmar` para ações irreversíveis. O domínio informado precisa existir em
  `CAMPOS_FEEDBACK` (`auth_state.py`).
- Registrar a rota com `ao_carregar(...)` para exibir o carregamento da página e
  declarar os campos da tela em `CAMPOS_LIMPEZA` para o botão **Limpar**.
- **Atualizar** recarrega os dados do Xano; **Limpar** só esvazia a tela e não
  exclui nada no servidor.
- Pontos de quebra (em largura CSS, já considerando a escala do Windows): menu de
  248 px a partir de 1536 px, 224 px de 1280 a 1535 px, trilho de ícones de 901 a
  1279 px e gaveta até 900 px. Formulários usam grade_campos e a classe
  gh-form-col, e listas devem manter base larga para o formulário empilhar em
  vez de cortar colunas.
- O painel lê totais (contagem do Xano, em paralelo, com cache de 60 s) e agrega os
  atendimentos no servidor (painel.py) em segundo plano; no navegador ficam só
  agregados e os 8 eventos mais recentes, nunca listas completas. Limiares dos
  alertas em painel.py.
- Listas paginadas pelo Xano (pacientes e médicos) usam listar_*_pagina,
  mudar_pagina e o rodapé paginacao; a busca vale só para a página exibida.
  Seletores de formulário que precisam de todos os registros usam as listas de
  referência (listar_todos_*), nunca a página exibida.
- Leituras ao Xano são repetidas só em GET (429, 502, 503, 504, conexão), com espera
  crescente (429 espera mais: `Retry-After` até 30 s ou 2 s, 4 s, 8 s, e abre uma pausa
  que vale para todas as threads); a conexão é compartilhada, há no máximo 3 requisições
  simultâneas e um limite por janela (`_Limitador`) que evita estourar a cota do Xano.
  Falhas de leitura registram-se com `_registrar_falha`: sessão recusada (401) leva ao
  login via `verificar_sessao` (disparado por `encerrar_acao`) e os demais erros
  mostram o botão **Tentar novamente** (`tentar_novamente`).
## Desenvolvimento

Mudanças são conduzidas via OpenSpec, seguindo o ciclo Explore → Propose →
Review → Apply → Archive. Veja `AGENTS.md` para as regras completas.
