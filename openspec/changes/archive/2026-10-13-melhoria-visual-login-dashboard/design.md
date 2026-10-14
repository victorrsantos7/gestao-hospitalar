# Design

## Context

O login atual usa os componentes Reflex existentes e está ligado diretamente ao
`AuthState`. O dashboard já apresenta os acessos condicionais por papel e os
botões redirecionam para rotas funcionais. Esta change deve alterar somente
composição, espaçamento, cores, tipografia e responsividade.

## Goals / Non-Goals

**Goals:**

- Criar uma composição visual dividida no login, com painel hospitalar e formulário.
- Melhorar hierarquia visual, foco, estados de erro e responsividade.
- Transformar o dashboard em uma superfície visual organizada, preservando os mesmos acessos.
- Usar imagem hospitalar como apoio visual sem depender de lógica de negócio.
- Preservar todos os nomes, textos, eventos, rotas, Vars e permissões atuais.

**Non-Goals:**

- Alterar autenticação, logout, sessão, autorização ou redirecionamentos.
- Alterar textos funcionais ou nomes de papéis.
- Criar métricas, consultas, cards de dados ou novas ações.
- Alterar Xano, State, endpoints ou modelo de dados.

## Decisions

### Login dividido

Usar um layout responsivo de duas colunas em desktop: painel visual hospitalar à
esquerda e formulário atual à direita. Em telas estreitas, o painel visual será
reduzido ou reorganizado acima do formulário para preservar o acesso aos campos.

A imagem será um asset visual remoto/estático contextualizado ao ambiente
hospitalar; nenhum texto do esboço será copiado para a aplicação. Os textos
atuais do sistema permanecem a fonte de verdade.

### Formulário preservado

Manter os mesmos componentes controlados, bindings de `AuthState`, evento
`do_login`, mensagem `erro` e botão de entrada. A mudança será feita apenas no
contêiner e nos estilos, evitando qualquer alteração no fluxo de autenticação.

### Dashboard organizado

Reorganizar os acessos já existentes em uma composição com cabeçalho, contexto
do usuário e grupos visuais de navegação. Cada botão continuará condicionado à
mesma Var de permissão e apontará para a mesma rota atual. O logout continuará
usando o mesmo evento.

### Validação visual

Validar desktop e mobile por compilação Reflex e inspeção visual no servidor
local. Confirmar login válido/inválido, logout, visibilidade por papel e
redirecionamentos para demonstrar que a mudança visual não alterou comportamento.

## Risks / Trade-offs

- **[Risco]** A imagem remota pode não carregar em uma rede restrita.
  **Mitigação:** manter contraste, fundo e formulário funcionais mesmo sem a imagem.
- **[Risco]** O layout visual pode ocultar campos em telas pequenas.
  **Mitigação:** usar dimensões responsivas e validar viewport móvel.
- **[Risco]** Uma reorganização pode esconder um acesso autorizado.
  **Mitigação:** reutilizar todas as condições e rotas atuais e comparar os quatro papéis.

## Migration Plan

1. Ajustar somente componentes de login e dashboard.
2. Compilar e executar a aplicação local.
3. Validar visualmente desktop/mobile e fluxos existentes por papel.
4. Arquivar e publicar sem alterações de backend ou dados.

## Open Questions

Nenhuma. O esboço visual foi tratado como referência de composição, sem copiar textos ou alterar comportamento.
