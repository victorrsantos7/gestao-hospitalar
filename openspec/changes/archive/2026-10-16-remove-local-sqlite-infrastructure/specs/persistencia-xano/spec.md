# Spec Delta

## MODIFIED Requirements

### Requirement: Comunicacao com a persistencia remota

O sistema MUST enviar e receber os dados de todos os fluxos funcionais por
requisições autenticadas ao Xano, MUST validar o formato das respostas antes de
usá-las e MUST NOT depender de banco de dados local ou fallback de persistência.

#### Scenario: Consulta remota bem-sucedida
- **WHEN** um fluxo funcional solicita dados e o Xano responde com sucesso
- **THEN** o sistema converte a resposta para o formato esperado pelo fluxo sem acessar persistência local

#### Scenario: Resposta remota invalida
- **WHEN** o Xano responde com dados ausentes ou em formato incompatível
- **THEN** o sistema rejeita a resposta, registra um erro técnico sem dados sensíveis e informa a indisponibilidade do fluxo

#### Scenario: Execução sem banco local
- **WHEN** a aplicação é compilada ou iniciada em um ambiente sem arquivo e sem configuração de banco local
- **THEN** os fluxos funcionais permanecem disponíveis por meio do Xano
