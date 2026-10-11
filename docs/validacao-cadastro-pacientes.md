# Validação do cadastro de pacientes

Data da última evidência: 11/10/2026.

## Resultado

| Cenário | Resultado | Evidência |
| --- | --- | --- |
| Cadastro válido | Confirmado | Requisição `POST /patients` retornou `201`. |
| CPF duplicado | Confirmado | Requisição `POST /patients` retornou `409`; o índice único foi aplicado. |
| Listagem autenticada | Confirmado | `medico`, `recepcionista` e `admin` autenticaram e receberam `200` em `GET /patients`. |
| Consulta detalhada | Confirmado | Usuário `medico` recebeu `200` em `GET /patients/1`. |
| Acesso sem sessão | Confirmado | A rota foi bloqueada pelo estado Reflex antes da consulta (`status=forbidden`). |
| CPF inválido no fluxo remoto | Confirmado | Usuário autorizado recebeu a mensagem `Informe um CPF valido.` e nenhum cadastro foi criado. |
| Criação por papel não autorizado | Confirmado | Usuário sem permissão foi impedido de cadastrar e nenhum novo registro foi criado. |

As evidências foram extraídas de `logs/gestao_hospitalar.log`, sem incluir
credenciais, tokens, CPF completo ou payloads de pacientes.

## Verificações locais

- `python -m unittest discover -s tests -v`: 20 testes aprovados.
- `python -m reflex compile --dry`: compilação aprovada.

Os dois cenários finais foram executados com usuários de teste, sem registrar
credenciais ou dados pessoais.