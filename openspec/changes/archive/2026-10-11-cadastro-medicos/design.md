# Design

## Context

O projeto já possui autenticação por Xano, autorização fixa, cliente HTTP,
estado Reflex e o fluxo de pacientes. A matriz atual já declara o recurso
`medicos` para recepcionista e admin, portanto a change deve reutilizar essa
decisão sem criar uma nova regra de papéis.

## Goals / Non-Goals

**Goals:**

- Implementar listagem, consulta e criação de médicos.
- Reutilizar o tratamento de erros e autenticação do cliente Xano.
- Validar e normalizar CRM, nome e telefone antes da escrita.
- Proteger rota, eventos e operações remotas com `pode_acessar`.

**Non-Goals:**

- Vincular médico a usuário ou permitir que médico edite o próprio cadastro.
- Criar agenda, atendimento ou diagnóstico.
- Criar permissões configuráveis ou alterar a matriz de papéis.

## Decisions

1. **Usar a matriz existente.** O recurso `medicos` será consultado pelo
   helper atual. Criar uma segunda regra específica na tela permitiria
   divergência entre interface e backend.
2. **Estender o cliente e estado existentes.** Métodos de médicos serão
   adicionados ao `XanoClient` e os eventos serão mantidos no `AuthState`,
   seguindo o padrão já usado para pacientes e evitando dois estados de sessão.
3. **Usar endpoints remotos em inglês.** A integração seguirá o padrão atual
   do Xano com `GET /doctors`, `GET /doctors/{doctor_id}` e `POST /doctors`.
4. **Normalizar CRM para comparação única.** A entrada aceitará de quatro a
   sete dígitos com UF e máscara brasileira, mas o valor enviado ao Xano será
   canonicalizado para evitar duplicidade por diferença de espaços, pontuação
   ou caixa.
5. **Manter a tela em rota própria.** A rota `/medicos` terá listagem,
   detalhes e formulário condicional; o dashboard exibirá o link somente para
   papéis autorizados, sem usar a visibilidade como mecanismo de segurança.

## Risks / Trade-offs

- **CRM possui variações regionais** -> validar quatro a sete dígitos e UF, mantendo a
  normalização centralizada e testes para entradas mascaradas.
- **Tabela ou endpoints ainda não publicados no Xano** -> validar o contrato
  remoto antes da integração e apresentar erro genérico sem quebrar a sessão.
- **Duplicidade concorrente** -> manter índice único no Xano e mapear resposta
  de conflito para a mesma mensagem de CRM duplicado.
- **Expansão indevida para atendimentos** -> manter os relacionamentos fora
  desta change; o médico será uma entidade consultável e independente.

## Migration Plan

1. Criar tabela e endpoints de médicos no ambiente Xano.
2. Implementar validador, cliente, estado e rota protegida.
3. Adicionar testes unitários, de contrato HTTP e de autorização.
4. Compilar, executar a suíte e validar manualmente os papéis autorizado e
   negado.
5. Rollback: remover a rota e os métodos de médicos sem alterar pacientes,
   usuários ou tokens existentes.