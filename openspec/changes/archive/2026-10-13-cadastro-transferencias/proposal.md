# Proposal

## Why

As internações já controlam o leito e o período do paciente, mas ainda não
registram sua movimentação entre setores do hospital. Sem transferências, a
jornada interna fica incompleta e a equipe perde o histórico de localização e
de motivo das mudanças.

## What Changes

- Criar transferências vinculadas a uma internação.
- Registrar data, destino e motivo da transferência.
- Permitir múltiplas transferências durante uma internação ativa.
- Permitir consulta do histórico de transferências da internação.
- Restringir criação e consulta a enfermagem/gestão e admin.
- Rejeitar transferências para internações inexistentes ou já encerradas.
- Manter o leito físico e sua ocupação fora da alteração automática nesta primeira versão.
- Manter edição e exclusão de transferências fora do escopo inicial.

## Capabilities

### New Capabilities

- `cadastro-transferencias`: registro e consulta da movimentação do paciente durante uma internação.

### Modified Capabilities

Nenhuma.

## Impact

- Nova tabela e endpoints protegidos no Xano.
- Novos métodos no cliente HTTP e estados/eventos Reflex.
- Nova seção na tela de internações para registrar e consultar transferências.
- Novos validadores de internação ativa, data, destino e motivo.
- A matriz existente já autoriza `transferencias` para enfermagem/gestão e admin.
- Controle de leitos e histórico consolidado permanecem nas capacidades existentes/futuras.
