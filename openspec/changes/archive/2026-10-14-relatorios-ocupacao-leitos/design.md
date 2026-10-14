# Design

## Context

Hoje `AuthState` carrega `self.leitos` e `self.internacoes` (listas de
`dict[str, str]`, já com todos os valores convertidos para string) para as
telas de cadastro de internações. Esses dados já contêm tudo que o
relatório precisa: `status` do leito (`livre`/`ocupado`), `status` da
internação (`internado`/`alta`) e `data_entrada` (ISO `aaaa-mm-dd`, vindo do
backend). Não há necessidade de nenhum novo endpoint Xano — ver proposal.md
para a decisão de escopo.

## Goals / Non-Goals

**Goals:**
- Reutilizar os dados já carregados pelas telas de internações/leitos,
  sem duplicar chamadas ao Xano.
- Isolar o cálculo de agregação (contagem de leitos, dias internado) em
  funções puras e testáveis, seguindo o padrão já usado pelos módulos
  `validacao_*.py` do projeto.
- Seguir o mesmo padrão visual/estrutural das demais telas (cards,
  `BOTAO_COMPACTO`, proteção de rota via `on_load` + redirect).

**Non-Goals:**
- Criar novo endpoint de agregação no Xano.
- Persistir ou cachear o relatório — ele é sempre recalculado a partir dos
  dados já carregados na sessão.
- Filtros, exportação ou paginação do relatório (candidatos a mudanças
  futuras).

## Decisions

- **Cálculo em módulo puro, não em `AuthState`**: criar
  `gestao_hospitalar/relatorios_calculo.py` com funções puras
  `contagem_leitos(leitos: list[dict]) -> dict` e
  `internacoes_ativas(internacoes: list[dict], hoje: date | None = None) ->
  list[dict]` (esta última já calculando `dias_internado`). `AuthState`
  expõe apenas computed vars (`resumo_leitos`, `internacoes_ativas`) que
  chamam essas funções sobre `self.leitos`/`self.internacoes`, já
  carregados por `carregar_internacoes`. Alternativa descartada: calcular
  tudo inline em computed vars do `AuthState` — funciona, mas mistura lógica
  de negócio com o State e dificulta testar sem instanciar Reflex, indo
  contra o padrão já usado no projeto (ver `validacao_internacoes.py`).
- **Reaproveitar o carregamento existente**: a página `/relatorios` usa
  `on_load=AuthState.carregar_internacoes` (o mesmo handler já usado por
  `/internacoes`), que já popula `self.leitos` e `self.internacoes`. Não é
  necessário criar um novo evento de carregamento.
- **`dias_internado` calculado com `date.today()`**: usa a data local do
  servidor (mesma abordagem de `validacao_internacoes.data_saida_valida`,
  que já compara datas ISO com `date.fromisoformat`). Não há fuso horário
  por paciente a considerar neste sistema.
- **Permissão via recurso existente, sem novo helper de autorização**:
  adicionar `RECURSO_RELATORIOS` ao `frozenset` de `enfermagem_gestao` e
  manter `admin` com acesso via wildcard `"*"`. `pode_ver_relatorios` em
  `AuthState` segue o mesmo padrão de `pode_ver_internacoes`
  (`self._pode_acessar_recurso(RECURSO_RELATORIOS)`).

## Risks / Trade-offs

- [Dado desatualizado se o usuário ficar muito tempo na tela sem recarregar]
  → Mitigação: aceitável para este primeiro relatório (mesma limitação já
  existente nas demais telas de listagem do sistema, que também não têm
  atualização automática).
- [Internações sem `data_entrada` válida quebrando o cálculo de dias]
  → Mitigação: `internacoes_ativas` ignora registros cuja `data_entrada`
  não seja uma data ISO válida (mesma validação defensiva usada em
  `validacao_internacoes.data_internacao_valida`), omitindo-os do relatório
  em vez de lançar exceção.
