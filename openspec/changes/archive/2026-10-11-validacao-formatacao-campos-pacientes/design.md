# Design

## Context

A tela de pacientes usa inputs Reflex controlados por `AuthState` e envia os
valores ao cliente Xano. O CPF já possui normalização e validação próprias,
mas telefone, contato de emergência, nome e data ainda dependem apenas do
preenchimento básico do formulário.

## Goals / Non-Goals

**Goals:**

- Manter valores controlados no `AuthState` e aplicar normalização antes do
  envio ao Xano.
- Exibir máscaras brasileiras sem armazenar pontuação no backend.
- Compartilhar as mesmas regras entre feedback da interface e validação do
  evento de criação.
- Cobrir regras de formato com testes determinísticos.

**Non-Goals:**

- Alterar tabela ou endpoints Xano.
- Suportar telefones internacionais.
- Validar endereço por geolocalização ou serviço externo.
- Criar edição ou exclusão de pacientes.

## Decisions

1. **Normalização no backend e máscara na interface.**
   A interface restringirá e formatará a entrada para feedback imediato, mas o
   `AuthState` repetirá a normalização e validação antes de chamar o Xano. Isso
   evita tratar a máscara como controle de segurança.

2. **CPF somente com 11 dígitos normalizados.**
   A rotina existente continuará responsável pelos dígitos verificadores; a
   camada de campo limitará a entrada a 11 dígitos e a apresentação usará
   `000.000.000-00`.

3. **Telefones brasileiros com 10 ou 11 dígitos.**
   Telefone e contato de emergência aceitarão somente dígitos, com limite de
   11 caracteres e validação final para 10 ou 11 dígitos. A apresentação usará
   máscara de telefone fixo ou celular conforme o comprimento.

4. **Nome com caracteres de pessoa.**
   O nome aceitará letras Unicode, espaços, hífen e apóstrofo, removendo
   espaços nas extremidades e rejeitando números ou símbolos não permitidos.

5. **Data real e não futura.**
   A data será validada como calendário real no formato recebido pelo input e
   comparada com a data atual no backend antes da chamada remota.

## Risks / Trade-offs

- **[Máscaras podem dificultar colagem]** -> aceitar texto colado, normalizar
  os dígitos e reaplicar a apresentação sem bloquear o fluxo.
- **[Nomes reais podem conter caracteres variados]** -> permitir Unicode,
  hífen e apóstrofo, mantendo a regra restrita apenas a números e símbolos
  incompatíveis.
- **[Data atual depende do ambiente]** -> usar a data local do servidor na
  validação final e cobrir datas-limite nos testes.

## Migration Plan

1. Criar helpers puros para nome, telefone, contato de emergência e data.
2. Ajustar setters e o evento de cadastro para normalizar e validar os campos.
3. Aplicar atributos e máscaras nos inputs Reflex.
4. Adicionar testes unitários e executar a compilação Reflex.
5. Validar manualmente entradas válidas e inválidas no navegador.
6. Nenhuma migração de dados ou alteração no Xano será necessária.
