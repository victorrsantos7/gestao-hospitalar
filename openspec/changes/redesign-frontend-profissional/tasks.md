# Tasks

## 1. Fundação visual

- [x] 1.1 Criar `gestao_hospitalar/ui/` com tema, ícones/marca SVG e componentes reutilizáveis; verificar importação e testes unitários dos auxiliares.
- [x] 1.2 Configurar `rx.theme`, reescrever `assets/styles.css` com tokens e fonte; verificar compilação.

## 2. Layout e navegação

- [x] 2.1 Criar layout com barra lateral, item ativo, barra superior e gaveta mobile; verificar navegação por papel.
- [x] 2.2 Migrar todas as páginas internas para o layout e remover "Voltar"; verificar rotas.

## 3. Feedback de ações

- [x] 3.1 Adicionar ação em andamento, notificação de resultado e busca ao `AuthState`; verificar com testes.
- [x] 3.2 Aplicar carregamento, toast, confirmação e erro persistente a todas as ações; verificar manualmente.

## 4. Telas

- [x] 4.1 Login com painel próprio em SVG e envio por Enter.
- [x] 4.2 Dashboard com indicadores por papel.
- [x] 4.3 Pacientes, médicos, convênios, atendimentos em tabelas com busca e detalhe.
- [x] 4.4 Internações, leitos e transferências com badges e confirmações.
- [x] 4.5 Histórico em linha do tempo.

## 5. Navegação, carregamento e controle da leitura

- [x] 5.1 Item ativo estático e fonte única `NAVEGACAO`; verificar tempo de destaque e teste de rotas/permissões.
- [x] 5.2 Esqueleto e aviso "Atualizando" durante `on_load`, com botões bloqueados até a hidratação.
- [x] 5.3 Botões Atualizar e Limpar em todas as telas de consulta; verificar com testes de estado e no navegador.

- [x] 5.4 Painel com contagens em paralelo, total de paginação do Xano, cache de 60 s e sem listas de pacientes no estado; verificar com testes de estado e do cliente.
- [x] 5.5 Paginação de pacientes e médicos, listas de referência do atendimento e checagem de CRM em todas as páginas; verificar com testes do cliente e do estado.
- [x] 5.6 Fonte Inter hospedada em `assets/fonts/` (sem Google Fonts); verificar o carregamento no navegador.

## 6. Validação final

- [x] 6.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile`.
- [x] 6.2 Validar visualmente desktop e mobile e confirmar login, logout, rotas e permissões sem regressão.
