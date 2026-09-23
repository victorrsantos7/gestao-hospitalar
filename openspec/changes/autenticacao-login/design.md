# Design

## Context

Ver proposal.md - Why. O projeto usa Reflex full-stack (`rx.State`,
`rx.Model`); ainda não existe nenhum usuário, modelo de autenticação ou
sessão implementados — esta é a primeira capability do projeto.

## Goals / Non-Goals

**Goals:**
- Permitir login/logout com sessão baseada em `rx.State`.
- Modelo de usuário com papel (recepcionista, médico, enfermagem/gestão)
  para uso em changes futuras de autorização.
- Proteger páginas internas contra acesso não autenticado.

**Non-Goals:**
- Autorização granular por papel (apenas o campo `papel` é armazenado;
  regras de permissão por papel ficam para changes futuras).
- Recuperação de senha ou cadastro de usuário via UI (usuários são
  inseridos via seed/admin inicial nesta change).
- Autenticação via terceiros (OAuth, SSO).

## Decisions

- **Sessão via `rx.State`**: o estado de autenticação (usuário logado) fica
  em um `AuthState` no backend Reflex, evitando dependências externas de
  sessão. Alternativa considerada: serviço de sessão externo — descartada
  por adicionar complexidade desnecessária nesta fase.
- **Senha com hash**: senhas são armazenadas com hash (`passlib`/`bcrypt`),
  nunca em texto aberto, conforme a regra de Security do
  `openspec/config.yaml`.
- **Novo `rx.Model` `Usuario`**: campos `id`, `login` (único), `senha_hash`,
  `papel`. Alternativa considerada: reaproveitar algum modelo existente —
  descartada porque não há nenhum modelo de usuário no domínio atual.
- **Rota de login como raiz**: a página de login substitui o `index`
  padrão gerado pelo `reflex init` na rota `/`. Páginas internas verificam
  `AuthState.is_authenticated` e redirecionam para `/login` quando falso.

## Risks / Trade-offs

- [Nenhum usuário inicial cadastrado] → Mitigação: incluir nas tasks a
  criação de um usuário administrador inicial via seed/migração.
- [Sessão baseada em `rx.State` pode se perder ao reiniciar o servidor em
  desenvolvimento] → Mitigação: aceitável nesta fase do projeto; revisar se
  necessário ao migrar para produção.

## Open Questions

- As regras de permissão específicas por papel (recepcionista, médico,
  enfermagem/gestão) não são definidas nesta change — apenas o campo
  `papel` é armazenado. A autorização por papel fica para uma change
  futura e não altera o escopo, a abordagem ou as tasks desta change.
