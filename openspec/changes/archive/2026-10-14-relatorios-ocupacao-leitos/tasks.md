# Tasks

## 1. Autorização

- [x] 1.1 Adicionar `RECURSO_RELATORIOS` ao `frozenset` de `enfermagem_gestao`
      em `PERMISSOES_POR_PAPEL` (`authorization.py`) e verificar com
      `tem_permissao("enfermagem_gestao", RECURSO_RELATORIOS) is True` e
      `tem_permissao("recepcionista", RECURSO_RELATORIOS) is False`.

## 2. Cálculo puro (testável sem Reflex)

- [x] 2.1 Criar `gestao_hospitalar/relatorios_calculo.py` com
      `contagem_leitos(leitos: list[dict]) -> dict` retornando
      `{"livres": int, "ocupados": int, "total": int}`.
- [x] 2.2 Implementar `internacoes_ativas(internacoes: list[dict], hoje:
      date | None = None) -> list[dict]`, filtrando apenas status
      `internado`, calculando `dias_internado` a partir de `data_entrada`
      (ISO) e ignorando registros com `data_entrada` inválida.
- [x] 2.3 Criar `tests/test_relatorios_calculo.py` cobrindo: leitos
      livres/ocupados/vazio, internações ativas com dias calculados,
      internação com alta excluída da lista, e `data_entrada` inválida
      ignorada sem lançar exceção. Verificar com
      `pytest tests/test_relatorios_calculo.py`.

## 3. Integração em `AuthState`

- [x] 3.1 Adicionar computed var `pode_ver_relatorios` em `auth_state.py`
      seguindo o padrão de `pode_ver_internacoes`
      (`self._pode_acessar_recurso(RECURSO_RELATORIOS)`).
- [x] 3.2 Adicionar computed vars `resumo_leitos` e
      `lista_internacoes_ativas` que chamam
      `relatorios_calculo.contagem_leitos(self.leitos)` e
      `relatorios_calculo.internacoes_ativas(self.internacoes)`
      respectivamente.
- [x] 3.3 Criar/atualizar `tests/test_auth_state_relatorios.py` cobrindo:
      `pode_ver_relatorios` true/false por papel, e que as computed vars
      refletem `self.leitos`/`self.internacoes` já carregados. Verificar
      com `pytest tests/test_auth_state_relatorios.py`.

## 4. Tela e rota

- [x] 4.1 Criar `gestao_hospitalar/relatorios.py` com a função de página
      `relatorios()`, reutilizando `BOTAO_COMPACTO`/padrão visual de card
      branco das demais telas, exibindo o resumo de leitos (contagens) e a
      lista de internações ativas (leito, data de entrada, dias
      internado), com mensagens para os casos vazios descritos no spec.
- [x] 4.2 Registrar a rota `/relatorios` em `gestao_hospitalar.py` com
      `on_load=AuthState.carregar_internacoes` (reaproveita o carregamento
      já existente de leitos/internações).
- [x] 4.3 Adicionar item de navegação "Relatórios" em `dashboard.py`,
      condicionado a `AuthState.pode_ver_relatorios`, e verificar
      manualmente (`reflex run`) que o item some/aparece conforme o papel
      logado.

## 5. Verificação final

- [x] 5.1 Rodar a suíte completa de testes (`pytest`) e confirmar que
      todos passam, incluindo os novos testes.
- [x] 5.2 Rodar `reflex compile` (ou equivalente) e confirmar que a
      aplicação compila sem erros.
- [x] 5.3 Testar manualmente no navegador: acessar `/relatorios` como
      `enfermagem_gestao`/`admin` (deve exibir o relatório) e como
      `recepcionista`/`medico` (deve redirecionar para `/dashboard`).
