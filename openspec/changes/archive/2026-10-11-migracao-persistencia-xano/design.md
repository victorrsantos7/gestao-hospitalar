# Design

## Context

A aplicacao atual usa Reflex com `rx.session()` e SQLModel para consultar o
usuario durante o login. A nova persistencia sera remota, mas os endpoints,
nomes dos recursos e formato final dos dados do Xano ainda dependem da
configuracao do workspace do grupo.

## Goals / Non-Goals

**Goals:**

- Isolar a comunicacao HTTP com o Xano em uma camada reutilizavel.
- Centralizar configuracao, autenticacao da API, timeout e mapeamento de erros.
- Adaptar primeiro a consulta de usuario usada pelo login.
- Permitir testes deterministas sem depender da rede.
- Delegar armazenamento e verificacao da senha ao recurso de autenticacao do
   Xano e evitar seu envio em logs ou mensagens.

**Non-Goals:**

- Implementar cadastro de pacientes ou outros recursos de dominio.
- Definir autorizacao por papel ou construir RBAC.
- Criar dashboard, financeiro ou relatorios.
- Inventar no codigo os endpoints e o esquema de dados do Xano antes da
  confirmacao do workspace.

## Decisions

1. **Cliente HTTP encapsulado em um adaptador de persistencia.**
   O estado Reflex nao fara chamadas HTTP diretamente. Um adaptador recebera
   configuracao e cliente de transporte, permitindo substituir o transporte
   por um fake nos testes. A alternativa de chamar HTTP dentro de cada State
   foi descartada por duplicar tratamento de erros e acoplar a UI ao Xano.

2. **Configuracao por ambiente.**
   URL base, token ou credencial da API e timeout serao lidos por configuracao
   externa. Nenhum segredo sera colocado em `rxconfig.py`, nos modelos ou no
   repositorio. A alternativa de valores default no codigo foi descartada por
   risco de vazamento e configuracao silenciosa incorreta.

3. **Erros tipados e mensagens genericas na interface.**
   O adaptador diferenciara configuracao ausente, timeout, indisponibilidade,
   autenticacao rejeitada e resposta invalida. A camada de fluxo convertera
   esses erros em mensagens sem tokens, senhas, payloads ou detalhes internos.

4. **Migracao incremental começando pela autenticacao.**
   O login sera o primeiro consumidor do adaptador, usando o endpoint de
   autenticacao do Xano. O Xano continua responsavel por armazenar e verificar
   a senha; a aplicacao recebe somente o identificador, o papel e o token da
   sessao. Os modelos e fluxos de dominio serao migrados em changes
   posteriores, quando seus contratos no Xano estiverem definidos.

5. **Sem fallback automatico para SQLite.**
   Depois de migrado um fluxo, falha no Xano nao redirecionara silenciosamente
   para o banco local. Isso evita divergencia de dados e resultados diferentes
   entre ambientes. Um mecanismo de contingencia somente sera criado em uma
   change propria.

## Risks / Trade-offs

- **[Contrato Xano ainda indefinido]** -> Confirmar endpoint, recurso, campos,
  formato de erro e mecanismo de autenticacao antes do apply.
- **[Indisponibilidade da rede impede o login]** -> Usar timeout curto, erro
  generico e testes de falha; nao mascarar o problema com fallback local.
- **[Escrita duplicada após timeout]** -> Comecar pela leitura do login e exigir
  idempotencia explicita antes de migrar operacoes de escrita.
- **[Dados sensiveis em logs]** -> Sanitizar excecoes e cobrir a politica com
  testes que verifiquem ausencia de senha e token.
- **[Dependencia de cliente externo]** -> Preferir o cliente HTTP ja presente
  no ambiente e adicionar dependencia somente se houver necessidade comprovada.

## Migration Plan

1. Confirmar no workspace Xano o endpoint, credencial, recursos e contratos do
   fluxo de consulta de usuario.
2. Adicionar configuracao externa validada e o adaptador coberto por testes.
3. Migrar o login para o endpoint de autenticacao do Xano e validar sucesso,
   credencial rejeitada, timeout e resposta invalida.
4. Executar a aplicacao sem depender do banco local no fluxo migrado.
5. Manter a configuracao SQLite apenas para fluxos ainda nao migrados, sem
   fallback cruzado dentro do fluxo de autenticacao.
6. Rollback: reverter o consumidor do login para a implementacao local e
   desativar as variaveis do Xano, sem apagar dados remotos.

## Contrato Xano Validado

- Instancia: `https://x8ki-letl-twmt.n7.xano.io`
- Workspace: `151596` (`Victor's Workspace`)
- Grupo de API: `Gestao Hospitalar`
- Canonical do grupo: `3lVm5Wbj`
- Tabela: `usuarios_hospital`
- Campos: `id`, `created_at`, `login`, `password`, `papel` e `ativo`.
- Papeis aceitos: `recepcionista`, `medico`, `enfermagem_gestao` e `admin`.
- Endpoint: `POST /api:3lVm5Wbj/auth/login`
- Entrada: `login` e `password`.
- Saida de sucesso: `authToken`, `user_id` e `papel`.
- Credenciais invalidas ou usuario inativo retornam erro generico de acesso.

## Open Questions

- O ambiente do grupo exige headers adicionais, allowlist de origem ou limite
  de requisicoes?
