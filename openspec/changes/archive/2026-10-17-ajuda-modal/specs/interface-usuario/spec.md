# interface-usuario Specification

## ADDED Requirements

### Requirement: Ajuda de uso em modal

O painel MUST oferecer um botão flutuante que abre, sem sair da página, um modal
com instruções de uso organizadas por módulo. O modal MUST listar apenas os
módulos que o perfil da pessoa pode acessar, além dos tópicos gerais (primeiros
passos, perfis e acessos, problemas comuns), e MUST poder ser fechado pelo botão
de fechar, pela tecla Esc ou clicando fora.

#### Scenario: Abrir a ajuda

- **WHEN** a pessoa aciona o botão de ajuda no painel
- **THEN** o modal abre no tópico "Primeiros passos" e a página continua a mesma

#### Scenario: Ajuda por perfil

- **WHEN** um usuário com perfil médico abre a ajuda
- **THEN** aparecem Pacientes e Atendimentos e diagnósticos, e não aparecem Internações e leitos nem Convênios

#### Scenario: Trocar de módulo

- **WHEN** a pessoa escolhe outro módulo na lista
- **THEN** o conteúdo à direita mostra as instruções desse módulo

#### Scenario: Tela estreita

- **WHEN** a largura da janela é menor que 640 px
- **THEN** a lista de módulos aparece como faixa rolável acima do conteúdo
