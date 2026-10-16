# Proposal

## Why

O painel tinha cartões grandes e desproporcionais (boas-vindas com três linhas,
indicadores largos e baixos com o ícone isolado, linhas incompletas) e mostrava
apenas totais. Faltava uma leitura da operação: tendência de atendimentos,
distribuição por tipo, atividade recente e avisos sobre ocupação e emergências.

## What Changes

- Layout compacto: boas-vindas em uma linha (58 px), indicadores de 68 px com o
  ícone ao lado do número, atalhos como lista enxuta.
- Gráfico "Atendimentos por período" (7 dias, 30 dias ou 12 semanas).
- "Atendimentos por tipo" (consulta, emergência, retorno) no período escolhido.
- "Ocupação de leitos" com porcentagem e barra (verde, âmbar a partir de 75%,
  vermelho a partir de 90%); substitui os cartões de leitos livres e ocupados.
- "Atividade recente": os 8 eventos mais novos entre atendimentos, internações e altas.
- Alertas: ocupação elevada/crítica, sem leitos livres ou poucos livres (2 ou
  menos) e emergências do dia.
- Leitura dos atendimentos em segundo plano: indicadores, ocupação e alertas
  aparecem primeiro e o gráfico, os tipos e a atividade entram em seguida, sem
  travar a navegação.
- Cada papel vê só os blocos que pode consultar.

Fora do escopo: novos endpoints no Xano, comparação com períodos anteriores e
filtros por médico ou convênio.

## Capabilities

### Modified Capabilities

- `interface-usuario`: indicadores e visão operacional do painel.

## Impact

- Novo módulo `painel.py` (cálculos puros) e `AuthState` (variáveis `painel_*`,
  `carregar_graficos` em segundo plano, `set_painel_periodo`).
- Cliente Xano: `listar_todos_atendimentos`.
- `dashboard.py`, `ui/componentes.py` (`metrica`, `icone_destaque`, `carregando`,
  `badge_status`) e `assets/styles.css`.