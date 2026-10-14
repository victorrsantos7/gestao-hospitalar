# Proposal

## Why

O sistema já controla leitos (livre/ocupado) e internações (internado/alta),
mas essa informação só existe espalhada em listas de cadastro
(`/internacoes`), sem nenhuma visão consolidada. Enfermagem/gestão e admin
não têm hoje uma tela que responda rapidamente "quantos leitos estão livres
agora?" e "quem está internado e há quanto tempo?" — perguntas recorrentes no
dia a dia hospitalar. O recurso `relatorios` já está reservado na matriz de
autorização (`authorization.py`), mas nunca foi implementado. Esta mudança
entrega o primeiro relatório operacional (ocupação de leitos + internações
ativas), estabelecendo o padrão de tela/permissão para relatórios futuros.

## What Changes

- Nova tela `/relatorios` com dois blocos:
  - **Ocupação de leitos**: contagem de leitos livres vs. ocupados e lista
    de leitos ocupados com o número do leito.
  - **Internações ativas**: lista de internações com status `internado`,
    mostrando leito, data de entrada e dias internado (calculado a partir
    da data de entrada até hoje).
- Dado agregado client-side a partir dos dados já carregados por
  `_carregar_leitos` e `_carregar_internacoes` (sem novo endpoint Xano nem
  agregação no backend).
- Liberar o recurso `RECURSO_RELATORIOS` para os papéis `enfermagem_gestao`
  e `admin` em `PERMISSOES_POR_PAPEL` (hoje só acessível via wildcard do
  admin).
- Adicionar item "Relatórios" na navegação lateral do dashboard, visível
  apenas para quem tem permissão (`pode_ver_relatorios`).
- Reaproveitar o padrão visual já estabelecido (cards brancos,
  `BOTAO_COMPACTO`, paleta azul) da mudança `melhoria-visual-modulos`.

**Fora do escopo desta mudança**: relatórios de atendimentos por
período/médico/convênio, relatórios financeiros (explicitamente fora do
escopo geral do projeto, ver `docs/project-overview.md`), exportação/impressão
de relatórios, e qualquer novo endpoint de agregação no Xano. Esses itens
ficam como candidatos para mudanças futuras de "Relatórios".

## Capabilities

### New Capabilities
- `relatorios-ocupacao-leitos`: relatório consolidado de ocupação de leitos
  e internações ativas, com controle de acesso por papel.

### Modified Capabilities
(nenhuma — os requisitos de `cadastro-leitos` e `cadastro-internacoes` não
mudam; esta mudança apenas lê os dados já expostos por eles.)

## Impact

- `gestao_hospitalar/authorization.py`: adicionar `RECURSO_RELATORIOS` aos
  papéis `enfermagem_gestao` e `admin`.
- `gestao_hospitalar/auth_state.py`: nova computed var `pode_ver_relatorios`
  e computed vars para os dados agregados (contagem de leitos por status,
  lista de internações ativas com dias internado).
- `gestao_hospitalar/relatorios.py` (novo): componente de tela.
- `gestao_hospitalar/gestao_hospitalar.py`: nova rota `/relatorios`.
- `gestao_hospitalar/dashboard.py`: novo item de navegação condicional.
- Testes: novo arquivo de testes para as computed vars/permissão em
  `tests/`.
