# Design

## Context

A sessão atual guarda `usuario_id` e `papel`, mas a proteção existente só
verifica se há sessão. O dashboard ainda é um placeholder e os módulos de
domínio não foram implementados. A matriz fixa aprovada pelo grupo deve ser
aplicada agora sem criar um sistema RBAC configurável.

## Goals / Non-Goals

**Goals:**

- Centralizar a decisão de autorização em uma matriz fixa no backend.
- Reutilizar a sessão Xano já estabelecida no login.
- Proteger páginas e eventos, não apenas esconder botões na interface.
- Encaminhar cada papel para uma home compatível.
- Tornar a autorização testável sem iniciar o servidor.

**Non-Goals:**

- Criar tabelas ou telas configuráveis de papel/permissão.
- Implementar cadastro de pacientes ou módulos ainda inexistentes.
- Criar financeiro e relatórios nesta change.

## Decisions

1. **Matriz fixa em código.**
   As permissões serão uma estrutura centralizada e imutável no backend. Isso
   atende ao escopo acadêmico e evita o custo de RBAC dinâmico. Uma tabela de
   permissões configurável foi descartada para não criar um módulo paralelo.

2. **Backend como autoridade.**
   Componentes Reflex podem ocultar navegação não autorizada, mas cada evento
   protegido deverá validar o papel novamente. Ocultar controles sem validar o
   evento permitiria acesso por chamada direta.

3. **Negação por padrão.**
   Papel vazio, desconhecido ou recurso não listado será rejeitado. Nenhuma
   nova funcionalidade receberá acesso automaticamente por ser adicionada à
   interface.

4. **Decorador/helper para eventos protegidos.**
   A implementação deverá concentrar a checagem de sessão e papel em um
   helper reutilizável, mantendo as funções de domínio pequenas e evitando
   verificações divergentes.

5. **Homes inicialmente compatíveis com o estado atual.**
   O dashboard existente poderá ser usado como shell inicial, com conteúdo e
   ações filtrados por papel. As páginas específicas só serão adicionadas nas
   changes dos respectivos módulos.

## Risks / Trade-offs

- **[Módulos futuros podem esquecer a checagem]** -> incluir autorização como
  requisito das próximas specs e testar cada evento protegido.
- **[Papel alterado no Xano durante uma sessão]** -> validar o papel no backend
  em cada operação sensível, sem confiar apenas na navegação carregada.
- **[Dashboard/financeiro/relatórios ainda não existem]** -> tratar o acesso
  como permissão planejada e não criar telas fora desta change.
- **[Matriz pode ficar desatualizada]** -> manter a matriz em um único módulo e
  exigir atualização de testes quando um novo papel for adicionado.

## Migration Plan

1. Criar a matriz e os helpers de autorização.
2. Aplicar a proteção à rota dashboard e ao redirecionamento pós-login.
3. Adicionar testes para os quatro papéis, papel desconhecido e sessão ausente.
4. Validar a aplicação e só então iniciar a change de cadastro de pacientes.
5. Rollback: remover as chamadas de autorização da navegação e manter o login
   Xano, sem alterar usuários ou dados remotos.
