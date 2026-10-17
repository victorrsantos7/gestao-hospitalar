# Tasks

## 1. Tela de login em celular

- [x] 1.1 Faixa `@media (max-width: 480px)`: painel vira uma faixa fina com só logo pequeno e nome, centralizados verticalmente (o conteúdo da faixa é centralizado porque o grid estica a linha do painel para preencher o viewport); sem título, frase nem destaques — testado trazer de volta título+frase (não cabe abaixo de ~640 px de altura) e o conteúdo completo (não cabe abaixo de ~700 px), então mantida só a versão compacta, única com margem confirmada em todas as alturas testadas (até 540 px). A marca duplicada do formulário some para não repetir a mesma informação. Validado em aparelho real (Galaxy S24): a 1ª tentativa (só ocultar os destaques) não coube; a 2ª (ocultar o painel inteiro) coube mas removeu todo traço de marca; esta 3ª versão (faixa compacta) atende as duas necessidades.
- [x] 1.2 Confirmar que a faixa de 481 a 900 px (painel reduzido, com destaques) e o layout de telas largas (≥ 901 px) continuam iguais.

## 2. Cabeçalho de cartão

- [x] 2.1 `secao()` com `wrap="wrap"` para o título descer para a linha de baixo quando a ação não couber ao lado.

## 3. Favicon

- [x] 3.1 Gerar `assets/favicon.ico` a partir da marca do sistema (16 a 256 px), substituindo o ícone padrão do Reflex.

## 4. Validação final

- [x] 4.1 Executar `python -m unittest discover -s tests -p "test_*.py"` e `reflex compile --dry`.
- [x] 4.2 Conferir visualmente a tela de login em 360–390 px (inclusive alturas reduzidas), 600, 1440 px com o servidor local (`reflex run`).
