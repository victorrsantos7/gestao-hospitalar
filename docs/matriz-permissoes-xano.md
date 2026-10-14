# Matriz de permissões do Xano

Esta matriz foi conferida contra `PERMISSOES_POR_PAPEL` e contra os endpoints
publicados no grupo **Gestão Hospitalar**. As permissões são aplicadas no Xano,
independentemente da visibilidade das telas no Reflex.

| Endpoints | recepcionista | médico | enfermagem_gestao | admin |
|---|---:|---:|---:|---:|
| `patients` GET e GET por ID | Sim | Sim | Não | Sim |
| `patients` POST, PATCH e DELETE | Sim | Não | Não | Sim |
| `doctors` GET, POST, PATCH e DELETE | Sim | Não | Não | Sim |
| `convenios` GET, POST, PATCH e DELETE | Sim | Não | Não | Sim |
| `atendimentos` GET e GET por ID | Sim | Sim | Não | Sim |
| `atendimentos` POST, PATCH e DELETE | Sim | Não | Não | Sim |
| `diagnosticos` GET e POST | Não | Sim | Não | Sim |
| `atendimentos/opcoes-internacao` GET | Não | Não | Sim | Sim |
| `internacoes` GET e POST | Não | Não | Sim | Sim |
| `internacoes/{id}/alta` POST | Não | Não | Sim | Sim |
| `leitos` GET e POST | Não | Não | Sim | Sim |
| `transferencias` POST e consulta por internação | Não | Não | Sim | Sim |
| Histórico do paciente e opções de histórico | Não | Não | Sim | Sim |

`auth/login` é o único endpoint sem sessão porque cria a sessão. Todos os
demais endpoints usam `auth = "usuarios_hospital"` e uma allowlist explícita de
papéis. Papel ausente ou desconhecido não satisfaz nenhuma allowlist e é negado
por padrão.

## Contas dedicadas de teste

Crie no Xano uma conta sem dados reais para cada papel:

- `recepcionista`;
- `medico`;
- `enfermagem_gestao`;
- `admin`.

Copie [`.env.example`](../.env.example) para `.env` e preencha somente as
variáveis `XANO_TEST_*` locais. Nunca versione o arquivo `.env`. A variável
`XANO_TEST_UNKNOWN_AUTH_TOKEN` é opcional e serve para uma conta de laboratório
com papel propositalmente não reconhecido; quando ela não existe, esse caso é
ignorado e a negação por padrão continua coberta pela auditoria da allowlist.

Execute os testes reais somente quando quiser acessar o ambiente remoto:

```powershell
$env:RUN_XANO_INTEGRATION = "1"
.\.venv\Scripts\python.exe -m unittest tests.test_xano_integration -v
```

Os testes executam apenas login e requisições GET. Nenhum registro é criado,
alterado ou excluído.
