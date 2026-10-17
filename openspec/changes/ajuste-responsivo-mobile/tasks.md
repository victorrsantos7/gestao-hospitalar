# Tasks

## 1. Tela de login em celular

- [x] 1.1 Faixa `@media (max-width: 480px)`: painel ilustrado oculto (a marca já aparece compacta no topo do formulário); verificar em 360 a 390 px de largura, inclusive com alturas reduzidas (até 580 px), sem rolagem até o botão "Entrar". Validado também em aparelho real (Galaxy S24) após a correção inicial (só ocultar os destaques) não ter sido suficiente.
- [x] 1.2 Confirmar que a faixa de 481 a 900 px (painel reduzido, com destaques) e o layout de telas largas (≥ 901 px) continuam iguais.

## 2. Cabeçalho de cartão

- [x] 2.1 `secao()` com `wrap="wrap"` para o título descer para a linha de baixo quando a ação não couber ao lado.

## 3. Favicon

- [x] 3.1 Gerar `assets/favicon.ico` a partir da marca do sistema (16 a 256 px), substituindo o ícone padrão do Reflex.

## 4. Validação final

- [x] 4.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 4.2 Conferir visualmente a tela de login em 360–390 px (inclusive alturas reduzidas), 600, 1440 px com o servidor local (`reflex run`).
