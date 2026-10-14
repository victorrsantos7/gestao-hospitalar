# Tasks

## 1. Levantamento e revisão

- [x] 1.1 Levantar strings visíveis sem acentuação nos componentes Reflex e `AuthState`, preservando símbolos e contratos técnicos.
- [x] 1.2 Corrigir títulos, botões, placeholders e mensagens para português brasileiro consistente.

## 2. Testes e validação

- [x] 2.1 Atualizar somente asserções de mensagens afetadas e verificar que não houve alteração funcional.
- [x] 2.2 Executar `python -m unittest discover -s tests -p "test_*.py"`, `reflex compile --dry` e `openspec validate revisao-textos-interface --strict`.
- [x] 2.3 Realizar revisão visual manual dos módulos e confirmar textos corrigidos antes do archive.
