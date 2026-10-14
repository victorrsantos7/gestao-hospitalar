# Spec Delta

## MODIFIED Requirements

### Requirement: Registro de atendimento autorizado

O sistema MUST permitir que recepcionista ou admin registre, edite e exclua um
atendimento com paciente, medico, data, motivo e tipo, podendo informar um
convenio. O backend MUST validar as referencias e os campos antes de
persistir qualquer uma dessas operacoes.

#### Scenario: Atendimento valido
- **WHEN** recepcionista ou admin envia paciente, medico, data, motivo e tipo validos
- **THEN** o sistema cria o atendimento, retorna seu identificador e confirma o registro

#### Scenario: Convenio opcional
- **WHEN** um usuario autorizado registra atendimento sem convenio
- **THEN** o sistema aceita o registro e mantem o vinculo de convenio vazio

#### Scenario: Papel sem permissao tenta registrar
- **WHEN** medico ou enfermagem/gestao tenta criar um atendimento
- **THEN** o backend rejeita a operacao e nao grava dados

#### Scenario: Edicao valida de atendimento
- **WHEN** recepcionista ou admin seleciona um atendimento existente e envia
  dados validos e completos para edicao
- **THEN** o sistema atualiza o registro no backend e exibe os dados
  atualizados na listagem e nos detalhes

#### Scenario: Exclusao de atendimento autorizada
- **WHEN** recepcionista ou admin solicita a exclusao de um atendimento existente
- **THEN** o sistema remove o registro somente apos confirmacao do servico
  remoto e atualiza a listagem

#### Scenario: Papel sem permissao tenta editar ou excluir
- **WHEN** medico ou enfermagem/gestao tenta editar ou excluir um atendimento
- **THEN** o backend rejeita a operacao e nao altera nem remove dados

### Requirement: Dados e referencias validos

O sistema MUST aceitar somente os tipos `consulta`, `emergencia` e `retorno`,
MUST exigir data, motivo, paciente e medico, e MUST rejeitar referencias que
nao existam ou estejam invalidas, tanto no cadastro quanto na edicao.

#### Scenario: Tipo invalido
- **WHEN** um usuario autorizado envia tipo diferente dos valores permitidos
- **THEN** o sistema rejeita o atendimento e informa erro de validacao

#### Scenario: Campo obrigatorio ausente
- **WHEN** um usuario autorizado envia atendimento sem data, motivo, paciente ou medico
- **THEN** o sistema rejeita o atendimento sem criar registro

#### Scenario: Referencia inexistente
- **WHEN** um usuario autorizado informa paciente, medico ou convenio inexistente
- **THEN** o sistema rejeita o atendimento sem criar vinculo parcial

#### Scenario: Edicao com referencia inexistente
- **WHEN** um usuario autorizado edita um atendimento informando paciente,
  medico ou convenio inexistente
- **THEN** o sistema rejeita a atualizacao sem alterar o registro original
