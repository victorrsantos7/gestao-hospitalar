# Design

## Context

O painel obtinha só contagens (paginação do Xano) e listas de leitos e
internações. Gráfico por período, tipos e atividade exigem os atendimentos com
data e tipo. O Xano não tem endpoint de agregação, e o `/atendimentos` devolve a
lista de registros.

## Decisions

### Agregar no servidor e guardar só agregados

`painel.py` reúne funções puras (testadas sem Reflex): série diária dos últimos
84 dias com zeros, recorte por período (7 e 30 dias diários; 12 semanas
semanais), totais por tipo, eventos de atividade e alertas. O estado guarda a
série (84 linhas), os 8 eventos mais recentes e a amostra lida; a lista completa
de atendimentos (com nomes) não vai para o navegador. Os 8 eventos exibem o nome
do paciente, informação a que os papéis com acesso a atendimentos já têm direito.

### Leitura em segundo plano

`carregar_graficos` é um evento `background=True` que lê os atendimentos em
`asyncio.to_thread` e só entra no estado para ler credenciais e gravar o
resultado. Assim a fila de eventos do usuário não espera a leitura: o painel
carrega indicadores e ocupação logo, e a navegação para outra página não é
bloqueada. Cache de 60 s (`VALIDADE_PAINEL_SEGUNDOS`); Atualizar força nova
leitura e Limpar invalida. Se o usuário sair no meio, o resultado é descartado.

### Total exato e amostra

O total de atendimentos continua vindo da contagem paginada. A série usa
`listar_todos_atendimentos`, que percorre páginas até 2000 registros; se a
amostra for menor que o total, o gráfico exibe a nota "consideram X de Y".
Evolução recomendada: endpoint de agregação por data no Xano.

### Alertas calculados, não armazenados

`painel_alertas` é variável calculada a partir de taxa de ocupação, leitos livres
e emergências do dia. Limiares em constantes (`OCUPACAO_ATENCAO=75`,
`OCUPACAO_CRITICA=90`, `MINIMO_LEITOS_LIVRES=2`). Sem livres, um alerta único
substitui o de ocupação.

### Layout

Indicadores compactos em grade `auto-fit`; análise e base em grade 2fr/1fr que
vira coluna única até 1100 px. Papéis sem atendimentos veem ocupação e
internações lado a lado; sem leitos, só os blocos de atendimentos.

## Risks / Trade-offs

- **[Risco]** Muitos atendimentos tornam a leitura lenta. **Mitigação:** segundo
  plano, cache de 60 s e limite de 2000 registros com aviso de amostra.
- **[Risco]** `date.today()` usa a data do servidor. **Mitigação:** aceitável para
  um painel de operação em um único fuso.

## Validation

Testes unitários de `painel.py`, das variáveis do estado e do cliente; no
navegador (produção, Xano simulado com 3 s de atraso): indicadores antes do
gráfico, barras por período, navegação em 159 ms durante a leitura, Atualizar e
Limpar, alertas por cenário e os três papéis.