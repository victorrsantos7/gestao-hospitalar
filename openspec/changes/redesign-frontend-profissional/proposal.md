# Proposal

## Why

O fluxo funcional está completo, mas a interface ainda é de aparência
amadora: não há design system (25 cores hexadecimais soltas apenas em login e
dashboard, tema padrão do Radix nas demais páginas), não há navegação
persistente entre módulos, listas são pilhas de cartões com texto "Rótulo:
valor", formulários usam o placeholder como rótulo e nenhuma ação dá retorno
visual de carregamento, sucesso ou erro além de um texto solto.

## What Changes

- Criar um design system único (tema Radix configurado no `RadixThemesPlugin`, tokens
  CSS, fonte Inter, paleta clínica azul-petróleo com cores semânticas).
- Criar um layout compartilhado com barra lateral fixa (ícones SVG, item
  ativo, gaveta no mobile) e barra superior com usuário e papel, aplicado a
  todas as páginas internas; o botão "Voltar" deixa de ser necessário.
- Dar feedback em toda ação: botão com indicador de carregamento e bloqueio
  contra duplo clique durante a chamada ao Xano, toast de sucesso/erro,
  confirmação antes de alta, exclusão e transferência, mensagem de erro
  persistente junto ao formulário, estados vazios ilustrados e esqueleto de
  carregamento enquanto a leitura chega.
- Botões Atualizar (recarrega do Xano) e Limpar (zera leitura, seleção, busca e
  formulário) nas telas de consulta; a leitura anterior continua visível ao
  voltar a uma tela, com aviso de atualização.
- Substituir listas de cartões por tabelas com busca, badges de status com
  cor semântica e histórico em linha do tempo.
- Dashboard com indicadores de leitura (totais e ocupação de leitos) obtidos por
  contagem em paralelo, sem trazer listas de pacientes ao navegador, com cache de
  60 s e respeitando as permissões do papel.
- Login sem dependência de imagem externa: painel próprio em SVG/gradiente.

Fora do escopo: regras de negócio, validações, matriz de autorização, cliente
Xano, contratos de dados, novos endpoints, modo escuro e internacionalização.

## Capabilities

### New Capabilities

- `interface-usuario`: padrões de navegação, feedback de ações e apresentação
  de dados da interface.

## Impact

- Novo pacote `gestao_hospitalar/ui/` (tema, ícones, componentes, layout).
- Reescrita visual de todas as páginas e de `assets/styles.css`.
- `AuthState`: apenas variáveis e eventos de apresentação (ação em andamento,
  notificação de resultado, termo de busca, indicadores do dashboard e listas
  filtradas). Nenhuma regra de negócio, validação ou autorização é alterada.
- Fonte Inter (SIL OFL) hospedada em `assets/fonts/`, sem dependência de rede
  externa.
- Paginação nas listas de pacientes e médicos (o Xano pagina esses endpoints),
  com listas de referência completas para o formulário de atendimentos.
