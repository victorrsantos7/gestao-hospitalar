# Tasks

## 1. Tela de login em celular

- [x] 1.1 Faixa `@media (max-width: 480px)`: texto do painel em fluxo normal (sem corte) e destaques ocultos; verificar em 375 e 390 px de largura sem rolagem até o botão "Entrar".
- [x] 1.2 Confirmar que a faixa acima de 480 px (até 900 px) e o layout de telas largas (≥ 901 px) continuam iguais.

## 2. Cabeçalho de cartão

- [x] 2.1 `secao()` com `wrap="wrap"` para o título descer para a linha de baixo quando a ação não couber ao lado.

## 3. Validação final

- [x] 3.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 3.2 Conferir visualmente a tela de login em 375, 390, 1440 px com o servidor local (`reflex run`).
