# Proposal

## Why

O sistema já autentica usuários, mas qualquer usuário autenticado consegue
alcançar a mesma área interna, sem validação do papel no backend. A matriz de
permissões foi definida pelo grupo e precisa ser aplicada antes do cadastro de
pacientes para proteger os fluxos clínicos e administrativos.

## What Changes

- Definir uma matriz fixa de permissões para recepcionista, médico,
  enfermagem/gestão e admin.
- Validar o papel no backend antes de liberar páginas e operações protegidas.
- Redirecionar usuários autenticados que não tenham permissão para uma área.
- Criar uma home adequada ao papel, preservando dashboard, financeiro e
  relatórios para gestão/admin conforme o escopo definido.
- Permitir que admin acesse todas as funcionalidades e gerencie usuários.
- Manter as permissões fixas no código, sem tela de RBAC configurável.

Fora do escopo: implementação do cadastro de pacientes, criação dos módulos
financeiro e relatórios, e modelagem de permissões configuráveis.

## Capabilities

### New Capabilities

Nenhuma.

### Modified Capabilities

- `autenticacao`: acrescentar autorização fixa por papel e restringir o acesso
  às áreas internas conforme a matriz aprovada.

## Impact

- Estado de autenticação e proteção das páginas Reflex.
- Componentes de navegação e home pós-login.
- Regras de autorização no backend para futuras operações de domínio.
- Especificação consolidada de autenticação.
- Testes dos quatro papéis e dos acessos negados.
