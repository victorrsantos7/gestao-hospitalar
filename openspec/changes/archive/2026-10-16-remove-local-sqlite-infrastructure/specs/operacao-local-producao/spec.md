# Spec Delta

## MODIFIED Requirements

### Requirement: Verificação prévia da apresentação

O sistema MUST oferecer uma verificação local reproduzível que valide ambiente
Python, dependências, configuração obrigatória, testes, compilação, porta de
execução e conectividade com o Xano antes de iniciar a apresentação. A
verificação MUST falhar com mensagem acionável quando um requisito essencial
não estiver pronto e MUST NOT exigir banco de dados ou migração local.

#### Scenario: Ambiente pronto
- **WHEN** o operador executa a verificação com ambiente, configuração e Xano disponíveis
- **THEN** o sistema confirma cada etapa e informa que a aplicação está pronta para iniciar sem criar ou consultar banco local

#### Scenario: Configuração ou dependência ausente
- **WHEN** a verificação encontra variável obrigatória, pacote ou porta em estado inválido
- **THEN** o sistema encerra com falha e informa exatamente como corrigir o item

#### Scenario: Execução restrita ao computador local
- **WHEN** a aplicação é iniciada para apresentação
- **THEN** ela fica acessível por `localhost` e não expõe involuntariamente seus serviços à rede local

### Requirement: Backup e restauração verificáveis

O projeto MUST oferecer backup versionado por data, salvo fora dos arquivos
rastreados pelo Git, com referência do commit, dependências, configuração sem
segredos e export do workspace Xano. O procedimento MUST possuir verificação de
integridade e instruções de restauração testadas com dados não sensíveis e MUST
NOT exigir nem incluir banco de dados local.

#### Scenario: Backup criado
- **WHEN** o operador executa o procedimento antes da apresentação
- **THEN** o sistema cria um pacote identificado por data com manifesto, hashes, metadados do repositório e export do Xano

#### Scenario: Segredo excluído do backup
- **WHEN** o pacote é inspecionado
- **THEN** ele não contém `.env`, bancos locais, senhas, tokens, logs nem credenciais do Xano

#### Scenario: Restauração ensaiada
- **WHEN** um backup de teste é restaurado em diretório temporário
- **THEN** os arquivos passam na verificação de integridade sem depender de validação SQLite e o roteiro informa como recuperar o ambiente

## REMOVED Requirements

### Requirement: Migração local consistente

**Reason**: A aplicação não possui modelos ou dados funcionais locais; todos os
fluxos persistem exclusivamente no Xano, tornando o banco e as migrações locais
infraestrutura sem uso.

**Migration**: Remover a configuração e os artefatos SQLite/Alembic, retirar as
verificações locais do preflight e manter o histórico das migrações somente no
Git e nas changes arquivadas.
