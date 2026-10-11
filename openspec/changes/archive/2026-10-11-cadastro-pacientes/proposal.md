# Proposal

## Why

O cadastro de pacientes é a primeira fatia funcional do domínio e fornece a
base para atendimentos, diagnósticos e internações. Com a autenticação e a
matriz de papéis em funcionamento, o sistema pode começar a registrar pacientes
com validação de CPF e proteção de dados no backend Xano.

## What Changes

- Criar a tabela `pacientes` no Xano com os dados cadastrais definidos no
  modelo de domínio.
- Criar APIs para listar, consultar e cadastrar pacientes.
- Implementar a tela Reflex de listagem e cadastro.
- Validar campos obrigatórios, formato de CPF e unicidade do CPF no backend.
- Permitir cadastro para recepcionista/admin e consulta para médico conforme a
  matriz de autorização.
- Evitar exposição desnecessária de contato de emergência e outros dados
  sensíveis na listagem.

Fora do escopo: edição e exclusão de pacientes, atendimentos, diagnósticos,
internações, convênios, médicos e histórico completo da jornada.

## Capabilities

### New Capabilities

- `cadastro-pacientes`: cadastro, consulta e listagem protegida de pacientes.

### Modified Capabilities

Nenhuma.

## Impact

- Workspace Xano: tabela `pacientes` e APIs do domínio.
- Cliente de persistência Xano e modelos de resposta.
- Estado e componentes Reflex para cadastro e listagem.
- Autorização fixa para diferenciar criação e consulta.
- Testes de CPF, duplicidade, permissões e dados sensíveis.
