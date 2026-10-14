# Tasks

## 1. Telas operacionais

- [x] 1.1 Padronizar visualmente Pacientes, Médicos e Convênios preservando controles, mensagens, eventos e rotas.
- [x] 1.2 Padronizar visualmente Atendimentos, Diagnósticos e detalhes relacionados sem alterar seus fluxos.
- [x] 1.3 Padronizar visualmente Internações/Leitos, Histórico e Transferências preservando ações e permissões.

## 2. Responsividade e consistência

- [x] 2.1 Aplicar espaçamentos, cores, painéis e grids responsivos consistentes em todos os módulos.
- [x] 2.2 Verificar que nenhum controle condicional desapareceu para recepcionista, médico, enfermagem/gestão ou admin.

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate melhoria-visual-modulos --strict`.
- [x] 3.2 Realizar revisão visual manual desktop/mobile e confirmar os fluxos por papel antes do archive.
