# Operação Local de Produção Specification

## Purpose

Garantir que a aplicação possa ser preparada, verificada, executada e
recuperada de forma previsível e segura no computador usado na apresentação.

## Requirements

### Requirement: Verificação prévia da apresentação

O sistema MUST oferecer uma verificação local reproduzível que valide ambiente
Python, dependências, configuração obrigatória, migrações, testes, compilação,
porta de execução e conectividade com o Xano antes de iniciar a apresentação.
A verificação MUST falhar com mensagem acionável quando um requisito essencial
não estiver pronto.

#### Scenario: Ambiente pronto
- **WHEN** o operador executa a verificação com ambiente, configuração, banco e Xano disponíveis
- **THEN** o sistema confirma cada etapa e informa que a aplicação está pronta para iniciar

#### Scenario: Configuração ou dependência ausente
- **WHEN** a verificação encontra variável obrigatória, pacote, migração ou porta em estado inválido
- **THEN** o sistema encerra com falha e informa exatamente como corrigir o item

#### Scenario: Execução restrita ao computador local
- **WHEN** a aplicação é iniciada para apresentação
- **THEN** ela fica acessível por `localhost` e não expõe involuntariamente seus serviços à rede local

### Requirement: Atualização controlada do Reflex

O projeto MUST avaliar uma nova versão do Reflex em ambiente isolado e somente
MUST atualizar as versões fixadas quando testes automatizados, compilação e
smoke test local passarem. Uma incompatibilidade MUST manter a versão atual
funcional e registrar a evidência da decisão.

#### Scenario: Nova versão compatível
- **WHEN** a versão candidata instala e passa em todas as verificações definidas
- **THEN** o projeto atualiza os pins relacionados e registra a versão validada

#### Scenario: Nova versão incompatível
- **WHEN** qualquer teste, compilação ou smoke test falha com a versão candidata
- **THEN** o projeto mantém a versão atual e documenta o erro sem comprometer o ambiente de apresentação

### Requirement: Migração local consistente

O sistema MUST manter as migrações Alembic alinhadas ao banco SQLite configurado
no Reflex, sem migrações vazias ou alterações destrutivas não revisadas. A
verificação MUST identificar divergência entre o histórico aplicado e os
scripts versionados antes da apresentação.

#### Scenario: Banco local atualizado
- **WHEN** o operador verifica um banco criado ou atualizado pelas migrações versionadas
- **THEN** o sistema confirma que não há revisão pendente nem mudança destrutiva inesperada

#### Scenario: Banco local divergente
- **WHEN** o banco possui schema diferente do histórico Alembic versionado
- **THEN** a verificação bloqueia a inicialização orientada e indica backup e correção antes de migrar

### Requirement: Integração real e não destrutiva com Xano

O projeto MUST possuir smoke tests opcionais contra o Xano real para validar
configuração, autenticação, rejeição de credenciais inválidas e consultas
essenciais autorizadas. Os testes MUST usar credenciais fornecidas por
variáveis de ambiente, MUST ser ignorados quando elas não existirem e não MUST
alterar dados permanentes. A execução contra o ambiente real MAY ser realizada
quando usuários dedicados estiverem disponíveis e não MUST bloquear a operação
local nem o arquivamento desta change.

#### Scenario: Integração habilitada
- **WHEN** credenciais de teste e URL do Xano são fornecidas explicitamente
- **THEN** os smoke tests validam autenticação e consultas essenciais sem criar, editar ou excluir registros

#### Scenario: Integração sem credenciais
- **WHEN** as credenciais de integração não estão configuradas
- **THEN** os testes são marcados como ignorados sem revelar segredo nem produzir falso sucesso

#### Scenario: Credenciais inválidas
- **WHEN** o teste envia credenciais inválidas
- **THEN** o Xano rejeita a autenticação e nenhuma sessão válida é criada

### Requirement: Autorização remota coerente e segura

Todos os endpoints protegidos do Xano MUST aplicar autorização por papel no
backend de forma coerente com a matriz da aplicação e MUST negar papéis não
previstos. Endpoints de escrita MUST aceitar somente campos explicitamente
permitidos e não MUST registrar senhas, tokens ou dados pessoais sensíveis.

#### Scenario: Papel permitido
- **WHEN** usuário autenticado chama endpoint compatível com seu papel
- **THEN** o backend executa a operação sem depender apenas da interface Reflex

#### Scenario: Papel não permitido
- **WHEN** usuário autenticado chama diretamente endpoint fora de sua permissão
- **THEN** o Xano rejeita a chamada sem ler ou modificar dados protegidos

#### Scenario: Campo interno enviado em atualização
- **WHEN** uma atualização inclui campo não autorizado como identificador, data interna ou atributo de autenticação
- **THEN** o backend rejeita ou ignora o campo sem alterar informação interna

#### Scenario: Log sem informação sensível
- **WHEN** autenticação e fluxos com dados pessoais são executados
- **THEN** logs locais e mensagens de erro não contêm senha, token, CPF, telefone, endereço ou contato de emergência

### Requirement: Backup e restauração verificáveis

O projeto MUST oferecer backup versionado por data, salvo fora dos arquivos
rastreados pelo Git, com banco SQLite, referência do commit, dependências,
configuração sem segredos e export do workspace Xano. O procedimento MUST
possuir verificação de integridade e instruções de restauração testadas com
dados não sensíveis.

#### Scenario: Backup criado
- **WHEN** o operador executa o procedimento antes da apresentação
- **THEN** o sistema cria um pacote identificado por data com manifesto e hashes dos arquivos incluídos

#### Scenario: Segredo excluído do backup
- **WHEN** o pacote é inspecionado
- **THEN** ele não contém `.env`, senhas, tokens, logs nem credenciais do Xano

#### Scenario: Restauração ensaiada
- **WHEN** um backup de teste é restaurado em diretório temporário
- **THEN** os arquivos passam na verificação de integridade e o roteiro informa como recuperar o ambiente

### Requirement: Inicialização e recuperação local documentadas

O sistema MUST possuir um procedimento de implantação local no Windows que
prepare o ambiente, inicie a aplicação em produção, grave logs, mostre a URL
correta e documente recuperação para porta ocupada, Xano indisponível e falha
de dependência.

#### Scenario: Inicialização bem-sucedida
- **WHEN** o operador executa o inicializador após a verificação prévia
- **THEN** a aplicação responde em `http://localhost:3000` e o log registra o início sem expor segredos

#### Scenario: Porta ocupada
- **WHEN** outro processo já utiliza a porta configurada
- **THEN** o inicializador identifica o PID responsável e orienta uma correção segura sem encerrar processos por nome

#### Scenario: Falha externa durante apresentação
- **WHEN** o Xano fica indisponível ou uma dependência falha
- **THEN** o runbook fornece diagnóstico, reinício e alternativa de demonstração sem corromper dados
