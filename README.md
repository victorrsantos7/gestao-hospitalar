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

## Desenvolvimento

Mudanças são conduzidas via OpenSpec, seguindo o ciclo Explore → Propose →
Review → Apply → Archive. Veja `AGENTS.md` para as regras completas.
