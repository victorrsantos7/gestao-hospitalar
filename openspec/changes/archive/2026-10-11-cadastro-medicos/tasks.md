# Tasks

## 1. Contrato remoto e validação

- [x] 1.1 Criar a tabela `doctors` e os endpoints protegidos no Xano; verificar manualmente respostas de listagem, detalhe, criação e conflito de CRM.
	- Tabela `doctors` e cinco endpoints publicados no workspace 151596; campos, índice único de CRM, autenticação e preconditions de papel verificados.
- [x] 1.2 Implementar normalização e validação de CRM, nome e telefone; verificar entradas válidas, inválidas e CRM duplicado com testes unitários.
- [x] 1.3 Adicionar `criar_medico`, `listar_medicos` e `consultar_medico` ao cliente Xano; verificar métodos, token de sessão e mapeamento de erros com transporte HTTP simulado.

## 2. Estado e autorização

- [x] 2.1 Adicionar campos e eventos de médicos ao estado Reflex; verificar carregamento, consulta, criação, limpeza do formulário e mensagens de erro.
- [x] 2.2 Aplicar `pode_acessar` ao recurso `medicos` em todos os eventos; verificar que recepcionista e admin podem operar e que médico/enfermagem/gestão são rejeitados no backend.
- [x] 2.3 Filtrar a navegação e o formulário pela matriz existente sem usar a interface como segurança; verificar que chamadas diretas continuam negadas.

## 3. Interface e integração

- [x] 3.1 Criar a rota `/medicos` com listagem, detalhe e formulário de cadastro; verificar a compilação da página e os estados vazio, carregando e erro.
- [x] 3.2 Adicionar o acesso autorizado ao dashboard e proteger a rota com sessão; verificar redirecionamento de sessão ausente e acesso por papel.
- [x] 3.3 Executar a suíte completa, `py_compile` e `reflex compile --dry`; confirmar que pacientes e autenticação continuam funcionando.
- [x] 3.4 Validar manualmente criação, consulta, duplicidade e tentativa negada com os papéis autorizados; registrar o resultado antes de iniciar convênios.
	- Cadastro válido, duplicidade de CRM, logout e acesso negado para medico/enfermagem_gestao foram confirmados manualmente.