# Proposal

## Why

O cadastro já valida CPF e campos obrigatórios no backend, mas a interface ainda aceita entradas fora do formato esperado e oferece pouco feedback imediato. Esta change melhora a qualidade dos dados e reduz erros de preenchimento antes do envio ao Xano.

## What Changes

- Aplicar máscara visual e limite de 11 dígitos ao CPF, aceitando somente números na entrada normalizada.
- Aplicar máscara brasileira ao telefone e ao contato de emergência, aceitando 10 ou 11 dígitos.
- Validar nomes para aceitar letras, acentos, espaços, hífen e apóstrofo, sem números.
- Validar data de nascimento como data real não futura.
- Repetir todas as regras no backend antes da chamada ao Xano.
- Adicionar testes unitários e validação manual dos campos.

Fora do escopo: alteração do schema Xano, edição/exclusão de pacientes, validação de endereço por serviço externo e suporte a telefones internacionais.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `cadastro-pacientes`: acrescentar regras observáveis de formato e validação dos campos cadastrais.

## Impact

- Estado e componentes Reflex da tela de pacientes.
- Funções de validação e normalização de dados cadastrais.
- Mensagens de validação exibidas na interface.
- Testes unitários e validação manual do formulário.
