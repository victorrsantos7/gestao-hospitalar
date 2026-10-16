# Spec Delta

## MODIFIED Requirements

### Requirement: Migração local consistente

O sistema MUST manter as migrações Alembic alinhadas ao banco SQLite
configurado no Reflex, sem migrações vazias ou alterações destrutivas não
revisadas. O schema local atualizado MUST estar na revisão versionada mais
recente e não MUST conter a tabela legada `usuario` nem seu índice. A remoção
dos registros dessa tabela MUST ocorrer sem backup, conforme decisão explícita
do responsável pelo ambiente. A verificação MUST identificar divergência entre
o histórico aplicado e os scripts versionados antes da apresentação.

#### Scenario: Banco local criado do zero

- **WHEN** um banco vazio recebe todas as migrações versionadas até a revisão mais recente
- **THEN** a revisão é registrada e a tabela `usuario` e seu índice não existem

#### Scenario: Banco local atualizado da revisão anterior

- **WHEN** um banco na revisão `d21af3eecf55` contém a tabela legada `usuario` e recebe a nova migração
- **THEN** todos os registros locais de usuário são descartados, a tabela e o índice são removidos sem backup e a revisão mais recente é registrada

#### Scenario: Banco local atualizado

- **WHEN** o operador verifica um banco na revisão mais recente e sem a tabela `usuario`
- **THEN** o sistema confirma que não há revisão pendente nem mudança destrutiva inesperada

#### Scenario: Banco local divergente

- **WHEN** o banco está em outra revisão ou ainda contém a tabela `usuario`
- **THEN** a verificação bloqueia a inicialização orientada e indica a aplicação da migração versionada
