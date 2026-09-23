# Project Overview — Sistema de Gestão Hospitalar

## 1. Visão geral

O Sistema de Gestão Hospitalar é uma aplicação web focada na **jornada do
paciente dentro do ambiente hospitalar**. O sistema permite cadastrar
pacientes, médicos e convênios, registrar atendimentos e diagnósticos,
controlar internações e ocupação de leitos, e rastrear a movimentação do
paciente entre as áreas do hospital.

## 2. Problema

Hospitais e clínicas enfrentam dificuldade em manter um histórico único e
organizado do paciente. Informações de atendimentos, diagnósticos,
internações e transferências ficam dispersas, dificultando o acompanhamento
da evolução do paciente e o controle da ocupação de leitos. Este sistema
resolve esse problema centralizando a gestão da jornada do paciente em uma
única aplicação.

## 3. Objetivos

- Centralizar o cadastro de pacientes, médicos e convênios.
- Registrar atendimentos e seus motivos de forma organizada.
- Controlar internações e a ocupação de leitos.
- Manter o histórico completo e rastreável do paciente, incluindo
  transferências entre áreas do hospital.

## 4. Público-alvo / usuários

- **Recepcionistas / administrativo**: cadastram pacientes, médicos e
  convênios, e registram atendimentos.
- **Médicos**: registram diagnósticos vinculados aos atendimentos.
- **Equipe de enfermagem / gestão**: controlam internações, leitos e
  transferências.

## 5. Escopo

O escopo inicial cobre a gestão da jornada do paciente:

- Cadastro de pacientes, médicos e convênios.
- Registro de atendimentos e motivos de consulta.
- Registro de diagnósticos por atendimento.
- Controle de internações e ocupação de leitos.
- Registro de transferências do paciente entre áreas do hospital.
- Visualização do histórico completo do paciente.

Fora do escopo inicial: faturamento, prescrição de medicamentos, agenda de
consultas, integração com sistemas externos e emissão de documentos legais.

## 6. Principais funcionalidades

- **Cadastro de pacientes**: nome, CPF, data de nascimento, telefone,
  endereço e contato de emergência.
- **Cadastro de médicos**: nome, CRM, especialidade e telefone.
- **Cadastro de convênios**: nome, tipo (particular, plano, SUS) e cobertura.
- **Registro de atendimentos**: vínculo entre paciente, médico e convênio,
  com data, motivo e tipo.
- **Registro de diagnósticos**: descrição e código CID vinculados ao
  atendimento.
- **Controle de internações**: entrada e saída do paciente, com vínculo a um
  leito.
- **Controle de leitos**: status livre/ocupado.
- **Registro de transferências**: movimentação do paciente com data e motivo.
- **Histórico do paciente**: linha do tempo de atendimentos, diagnósticos,
  internações e transferências.

## 7. Requisitos e restrições importantes

- CPF do paciente e CRM do médico devem ser únicos.
- Um leito só pode estar ocupado por um paciente por vez.
- Nem todo atendimento gera internação.
- Uma internação pode ter múltiplas transferências.
- Validação de campos obrigatórios no backend.

## 8. Arquitetura tecnológica

- **Stack**: Reflex (Python full-stack) — frontend e backend implementados
  na mesma base de código Python, sem tecnologias adicionais de frontend
  (nada de HTML/JS/templates separados).
- **Persistência**: modelos Reflex (`rx.Model`) sobre banco relacional —
  SQLite em desenvolvimento, com possibilidade de migração para MySQL.
- **Padrão**: organização por `State` (`rx.State`) e `Components` do
  Reflex, substituindo o padrão MVC tradicional.

## 9. Princípios de desenvolvimento

- Desenvolvimento incremental utilizando OpenSpec.
- O modelo conceitual é global; a implementação física é incremental.
- Mudanças devem ser especificadas antes da implementação.
- O grupo revisa e aprova as propostas do agente antes da implementação.

## 10. Segurança e integridade

- Validação de entradas no backend.
- Regras de autorização aplicadas no backend.
- Proteção de dados sensíveis dos pacientes.
- Integridade referencial garantida pelo banco relacional.

## 11. Estratégia de desenvolvimento

O desenvolvimento será conduzido em mudanças incrementais (changes) via
OpenSpec, seguindo o ciclo Explore → Propose → Review → Apply → Archive.
A primeira fatia funcional prioriza o cadastro de pacientes, seguido de
médicos, convênios, atendimentos, internações e transferências.

## 12. Fonte de verdade e documentação

- `docs/project-overview.md` — visão geral (este documento).
- `docs/domain-model.md` — modelo de domínio.
- `AGENTS.md` — regras de trabalho dos agentes.
- `openspec/config.yaml` — contexto e regras dos workflows.
- `openspec/specs/` — comportamento consolidado do sistema.
- `openspec/changes/` — mudanças em andamento e histórico.