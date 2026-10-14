# Design

## Context

O login e o dashboard já receberam uma linguagem visual hospitalar. As telas
operacionais ainda usam cards e estruturas independentes. Esta change deve
padronizar a apresentação sem tocar nos contratos funcionais.

## Goals / Non-Goals

**Goals:**

- Aplicar uma moldura visual consistente às telas internas.
- Melhorar hierarquia de títulos, formulários, listas, detalhes e mensagens.
- Preservar todas as condições de autorização e eventos atuais.
- Manter layouts legíveis em desktop e mobile.

**Non-Goals:**

- Alterar textos funcionais, regras, endpoints ou State.
- Criar novas métricas, filtros, pesquisas ou ações.
- Alterar a estrutura visual do login/dashboard já finalizada nesta etapa.

## Decisions

### Linguagem visual compartilhada

Usar fundo claro, painéis brancos, bordas suaves, azul-marinho para títulos e
navegação, azul hospitalar para ações e estados de destaque, além de mensagens
semânticas para erro/sucesso. O mesmo padrão será aplicado a todas as telas.

### Componentes existentes

Reorganizar os componentes atuais com `rx.vstack`, `rx.hstack`, `rx.card`,
grid responsivo e espaçamentos consistentes. Nenhum evento será substituído;
os mesmos callbacks e Vars permanecerão ligados aos controles.

### Fluxo de telas

Manter cabeçalho com título e retorno ao dashboard, formulários em painéis de
trabalho, listas em itens escaneáveis e detalhes em seções claramente separadas.
A tela de internações continuará exibindo histórico de transferências e ações
existentes, apenas com nova composição.

### Verificação

Executar testes funcionais, compilação Reflex e inspeção visual desktop/mobile.
Comparar permissões por papel e confirmar que todos os botões continuam levando
às mesmas rotas.

## Risks / Trade-offs

- **[Risco]** Uma reorganização pode ocultar uma ação existente.
  **Mitigação:** preservar todos os componentes condicionais e revisar cada rota.
- **[Risco]** Painéis podem ficar densos em telas pequenas.
  **Mitigação:** usar largura relativa, grids adaptáveis e empilhamento responsivo.
- **[Risco]** Diferenças entre módulos podem gerar inconsistência.
  **Mitigação:** aplicar tokens visuais e padrões de cabeçalho/lista/formulário em todos.

## Migration Plan

1. Reformular visualmente cada módulo sem mudar sua lógica.
2. Compilar e executar testes após a aplicação do padrão.
3. Validar manualmente os fluxos por papel.
4. Arquivar e publicar sem tocar em dados ou backend.

## Open Questions

Nenhuma.
