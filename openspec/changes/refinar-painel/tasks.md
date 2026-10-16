# Tasks

## 1. Cálculos e estado

- [x] 1.1 `painel.py`: série, períodos, tipos, atividade e alertas; verificar com testes unitários.
- [x] 1.2 Cliente: `listar_todos_atendimentos`; verificar paginação e normalização.
- [x] 1.3 Estado: variáveis `painel_*`, `carregar_graficos` em segundo plano, período, limpeza e logout; verificar com testes.

## 2. Interface

- [x] 2.1 Indicadores compactos, boas-vindas em uma linha e ocupação com barra.
- [x] 2.2 Gráfico por período, tipos, atividade recente, alertas e acessos.
- [x] 2.3 Layout por papel (administrador, recepcionista, enfermagem).

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 3.2 Validar no navegador: carga em duas etapas, períodos, navegação durante a leitura, Atualizar, Limpar e alertas.