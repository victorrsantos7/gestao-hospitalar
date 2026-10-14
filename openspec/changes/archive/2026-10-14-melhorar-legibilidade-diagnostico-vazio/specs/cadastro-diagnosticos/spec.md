# Spec Delta

## ADDED Requirements

### Requirement: Estado vazio legível

O sistema MUST exibir a mensagem de ausência de diagnósticos com contraste
suficiente para leitura sobre o fundo da área de detalhes do atendimento.

#### Scenario: Atendimento sem diagnósticos

- **WHEN** médico ou admin consulta um atendimento que não possui diagnósticos
- **THEN** o sistema exibe "Nenhum diagnóstico encontrado." com cor leve e legível
