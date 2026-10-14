# Tasks

## 1. Limpeza segura da tentativa anterior

- [x] 1.1 Registrar em backup externo o pull atual do Xano e o diff local antes da limpeza, verificando que `.env`, tokens e logs não foram incluídos
- [x] 1.2 Remover por nome somente os oito endpoints Xano de edição/exclusão criados pela change `edicao-exclusao-fluxos-hospitalares` e confirmar com novo pull que os demais endpoints permanecem inalterados
- [x] 1.3 Remover somente as adições locais não integradas de cliente/testes associadas aos oito endpoints, preservando todas as demais mudanças locais e verificando o diff arquivo a arquivo
- [x] 1.4 Registrar o cancelamento e retirar a change `edicao-exclusao-fluxos-hospitalares` da lista ativa sem sincronizar suas specs, confirmando `openspec list`

## 2. Segurança e permissões

- [x] 2.1 Corrigir no Xano os endpoints POST/PATCH/DELETE de Convênios para exigir recepcionista ou admin e confirmar por pull que as preconditions foram publicadas
- [x] 2.2 Corrigir no Xano os endpoints POST/PATCH/GET de Médicos para exigir recepcionista ou admin, substituindo o PATCH de corpo bruto por campos explícitos, e confirmar por pull a publicação sem mass assignment
- [x] 2.3 Auditar todos os endpoints do grupo Gestão Hospitalar contra `PERMISSOES_POR_PAPEL`, registrar a matriz endpoint × papel e verificar negação por padrão
- [x] 2.4 Corrigir o envio opcional de `XANO_API_TOKEN` para usar o valor configurado sem exibi-lo e verificar com teste de request e varredura de logs
- [x] 2.5 Criar gate de segurança que falhe se `.env`, `*.db`, `*.log`, backups ou exports Xano forem rastreados e verificar o repositório atual
- [x] 2.6 Executar fluxo com valores-sentinela e confirmar que senha, token, CPF, telefone, endereço e contato de emergência não aparecem em logs

## 3. Integração real com Xano

- [x] 3.1 Definir variáveis `XANO_TEST_*` no `.env.example` sem valores reais e documentar a criação de usuários dedicados para os quatro papéis
- [x] 3.2 Criar smoke tests opt-in para login válido/inválido e consultas essenciais não destrutivas, verificando skip quando faltarem credenciais
- [x] 3.3 Criar testes de autorização reais para papéis permitidos e negados nos endpoints críticos, incluindo papel desconhecido e token inválido, sem alterar registros

## 4. Migrações e banco local

- [x] 4.1 Revisar `rxconfig.py`, `alembic.ini`, `alembic/env.py` e a revisão inicial, documentando que Alembic gerencia somente o SQLite local
- [x] 4.2 Alinhar a URL/metadata da migração ao banco Reflex sem segredo ou URL fictícia e verificar `alembic current`, `heads` e `history`
- [x] 4.3 Criar um banco SQLite temporário desde zero, executar todas as migrações e verificar schema e índices esperados
- [x] 4.4 Copiar o banco local para área temporária, verificar upgrade sem perda de dados e somente então registrar o procedimento aplicável ao banco principal
- [x] 4.5 Eliminar ou documentar de forma acionável o aviso `Detected database schema changes`, sem gerar migração vazia

## 5. Atualização controlada do Reflex

- [x] 5.1 Identificar a versão estável candidata e suas notas de migração, registrando incompatibilidades relevantes para os componentes/plugins usados
- [x] 5.2 Criar ambiente virtual temporário, instalar o manifesto com a versão candidata e verificar resolução completa de dependências
- [x] 5.3 No ambiente temporário, executar suíte completa, `reflex compile --dry` e smoke test HTTP local, registrando resultados
- [x] 5.4 Atualizar os pins do Reflex somente se todos os gates passarem; caso contrário manter `0.9.12` e documentar o motivo, verificando que o ambiente principal permanece funcional

## 6. Backup e restauração

- [x] 6.1 Criar script Windows de backup para pasta externa configurável, incluindo SQLite, commit/diff, dependências, configurações sem segredo e export Xano sem registros
- [x] 6.2 Gerar manifesto com timestamp e hashes SHA-256 e verificar integridade dos arquivos do pacote
- [x] 6.3 Garantir por teste que `.env`, credenciais, logs e caches não entram no backup
- [x] 6.4 Criar e executar ensaio de restauração em diretório temporário, verificando hashes, banco SQLite e passos de recuperação
- [x] 6.5 Documentar a limitação do backup remoto do Xano e o procedimento administrativo necessário para exportar registros quando aplicável

## 7. Implantação local para apresentação

- [x] 7.1 Criar script de preflight somente leitura para ambiente, dependências, configuração, Git, migrações, testes, compilação, porta e conectividade Xano, verificando sucesso e falhas acionáveis
- [x] 7.2 Ajustar o inicializador para depender do preflight aprovado, usar loopback/`localhost`, gravar logs e não exibir segredos
- [x] 7.3 Detectar porta 3000 ocupada e informar PID/comando seguro de diagnóstico sem encerrar processos automaticamente
- [x] 7.4 Criar runbook de apresentação com ordem de backup, preflight, início, URL, contas de teste, roteiro funcional, reinício e troubleshooting
- [x] 7.5 Verificar CORS HTTP/WebSocket e exposição de portas, confirmando que origens hostis e máquinas da rede local não acessam o serviço
- [x] 7.6 Executar ensaio completo em ambiente limpo do computador: backup → preflight → início → smoke tests → encerramento → restauração

## 8. Validação final

- [x] 8.1 Executar suíte completa de testes e confirmar todos os testes unitários e de segurança passando
- [x] 8.2 Executar `reflex compile --dry` no ambiente definitivo e confirmar sucesso
- [x] 8.3 Executar `openspec validate preparacao-apresentacao-producao --strict` e confirmar a change válida
- [x] 8.4 Revisar o diff para confirmar que nenhum módulo funcional foi alterado fora do escopo e preparar checklist final da apresentação
