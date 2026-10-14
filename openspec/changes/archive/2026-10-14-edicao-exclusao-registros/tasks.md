# Tasks

## 1. Backend Xano — endpoints de edição e exclusão

- [x] 1.1 Fazer `xano workspace pull` para a workspace do projeto e localizar
      `api/gestao_hospitalar/patients/`, `api/gestao_hospitalar/atendimentos/`
      e `api/gestao_hospitalar/doctors/` como referência de padrão
- [x] 1.2 Criar `patients_id_PATCH.xs` (edição) e `patients_id_DELETE.xs`
      (exclusão) para `patients`, seguindo o padrão de
      `doctors_id_PATCH.xs`/`doctors_id_DELETE.xs`: precondition restringindo
      a `recepcionista`/`admin`, e no DELETE verificar se existem
      atendimentos/diagnósticos/internações vinculados ao paciente antes de
      remover, retornando erro de validação quando houver vínculo
- [x] 1.3 Criar `atendimentos_id_PATCH.xs` (edição) e `atendimentos_id_DELETE.xs`
      (exclusão) para `atendimentos`, com a mesma precondition de papel e,
      no DELETE, verificar se existe internação vinculada ao atendimento
      antes de remover
- [x] 1.4 Validar os `.xs` criados com `xano_validate_xanoscript` e confirmar
      ausência de erros de sintaxe
- [x] 1.5 Fazer `xano workspace push` (modo parcial) e confirmar no preview
      que apenas os arquivos novos/alterados serão enviados
- [x] 1.6 Testar manualmente os 4 novos endpoints (via UI ou chamada direta)
      confirmando que papéis sem permissão recebem erro de acesso negado
      (feito junto com 7.3, com a UI de edição/exclusão já existente)

## 2. Cliente Xano (`xano_client.py`)

- [x] 2.1 Adicionar `atualizar_paciente` e `excluir_paciente`, espelhando
      `atualizar_convenio`/`excluir_convenio`, e cobrir com teste unitário
      verificando o verbo HTTP e a URL chamados
- [x] 2.2 Adicionar `atualizar_medico` e `excluir_medico` da mesma forma
- [x] 2.3 Adicionar `atualizar_atendimento` e `excluir_atendimento` da mesma
      forma

## 3. Estado da aplicação (`auth_state.py`) — Pacientes

- [x] 3.1 Adicionar campo `id_paciente_edicao` e reaproveitar os campos de
      formulário de paciente já existentes (nome, CPF, data de nascimento,
      telefone, endereço, contato de emergência)
- [x] 3.2 Implementar `editar_paciente(paciente_id)` (preenche o formulário
      com o registro selecionado) e `cancelar_edicao_paciente()` (limpa o
      formulário), com teste cobrindo os dois fluxos
- [x] 3.3 Adaptar `salvar_paciente` para criar quando `id_paciente_edicao`
      estiver vazio e atualizar (revalidando CPF único excluindo o próprio
      registro) quando estiver preenchido, com testes cobrindo ambos os
      casos e o caso de CPF duplicado na edição
- [x] 3.4 Implementar `excluir_paciente(paciente_id)` checando permissão,
      chamando `excluir_paciente` do cliente Xano e recarregando a listagem,
      com teste cobrindo sucesso, falha de permissão e falha por vínculo
      existente

## 4. Estado da aplicação (`auth_state.py`) — Médicos

- [x] 4.1 Adicionar campo `id_medico_edicao` reaproveitando os campos de
      formulário de médico já existentes (nome, CRM, especialidade, telefone)
- [x] 4.2 Implementar `editar_medico(medico_id)` e `cancelar_edicao_medico()`,
      com teste cobrindo os dois fluxos
- [x] 4.3 Adaptar `salvar_medico` para criar ou atualizar conforme
      `id_medico_edicao`, revalidando CRM único excluindo o próprio registro
      na edição, com testes cobrindo criação, atualização e CRM duplicado
- [x] 4.4 Implementar `excluir_medico(medico_id)` com teste cobrindo sucesso
      e falha de permissão

## 5. Estado da aplicação (`auth_state.py`) — Atendimentos

- [x] 5.1 Adicionar campo `id_atendimento_edicao` reaproveitando os campos de
      formulário de atendimento já existentes (paciente, médico, convênio,
      data, motivo, tipo)
- [x] 5.2 Implementar `editar_atendimento(atendimento_id)` e
      `cancelar_edicao_atendimento()`, com teste cobrindo os dois fluxos
- [x] 5.3 Adaptar `salvar_atendimento` para criar ou atualizar conforme
      `id_atendimento_edicao`, revalidando tipo e referências (paciente,
      médico, convênio) na edição, com testes cobrindo criação, atualização
      e referência inexistente
- [x] 5.4 Implementar `excluir_atendimento(atendimento_id)` com teste
      cobrindo sucesso, falha de permissão e falha por internação vinculada

## 6. Interface — Pacientes, Médicos e Atendimentos

- [x] 6.1 Adicionar botões "Editar" e "Excluir" por linha na tabela de
      Pacientes (`pacientes.py`), reaproveitando `BOTAO_COMPACTO` de
      `estilos.py`, e exibir o formulário em modo de edição quando
      `id_paciente_edicao` estiver preenchido
- [x] 6.2 Repetir o mesmo padrão em Médicos (`medicos.py`)
- [x] 6.3 Repetir o mesmo padrão em Atendimentos (`atendimentos.py`)
- [x] 6.4 Adicionar confirmação antes de excluir (mesmo padrão usado em
      Convênios) nos três módulos

## 7. Validação final

- [x] 7.1 Rodar a suíte completa de testes
      (`python -m unittest discover -s tests -p "test_*.py"`) e confirmar que
      todos passam
- [x] 7.2 Rodar `reflex compile` e confirmar sucesso
- [x] 7.3 Testar manualmente os três módulos com papel `recepcionista`/`admin`
      (editar e excluir com sucesso) e com `medico`/`enfermagem_gestao`
      (acesso negado), confirmando visualmente no navegador
- [x] 7.4 Rodar `openspec validate edicao-exclusao-registros --strict` e
      confirmar sucesso antes do archive
