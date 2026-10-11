# Tasks

## 1. Contrato e configuracao

- [x] 1.1 Confirmar no workspace Xano a URL base, mecanismo de autenticacao, recurso de usuarios, campos e formato de erros; registrar o contrato validado na change.
- [x] 1.2 Definir as variaveis de ambiente documentadas para URL, credencial opcional e timeout, e verificar que a aplicacao falha claramente quando uma variavel obrigatoria esta ausente.
- [x] 1.3 Definir uma politica de sanitizacao de logs e verificar por teste que token, senha e payload sensivel nao aparecem em erros.

## 2. Adaptador de persistencia

- [x] 2.1 Criar o modulo de acesso ao Xano com cliente de transporte injetavel e verificar chamadas autenticadas no teste unitario.
- [x] 2.2 Implementar validacao das respostas e mapeamento de configuracao ausente, timeout, indisponibilidade, erro de autenticacao e resposta invalida; verificar cada caso com testes.
- [x] 2.3 Cobrir leitura bem-sucedida e falha de escrita sem repeticao automatica quando o resultado for desconhecido; verificar a regra de integridade com testes.

## 3. Migracao do login

- [x] 3.1 Adaptar o login para o endpoint de autenticacao do Xano, mantendo a senha sob responsabilidade do Xano e retornando apenas dados publicos da sessao; verificar login valido e invalido.
- [x] 3.2 Verificar que falhas do Xano produzem mensagem generica para o usuario e nao deixam fallback silencioso para SQLite.
- [x] 3.3 Atualizar a configuracao da aplicacao e dependencias somente quando necessario, verificando que o fluxo migrado nao depende do banco local.

## 4. Validacao da integracao

- [x] 4.1 Executar a suite de testes da integracao com transporte falso e verificar cenarios de sucesso, timeout, credencial rejeitada e resposta invalida.
- [x] 4.2 Executar verificacao do Reflex e um teste manual do login contra um ambiente Xano de teste, confirmando que nenhum segredo aparece na interface ou nos logs.
- [x] 4.3 Atualizar a documentacao de arquitetura e o resumo de decisoes para refletir a persistencia Xano somente apos a validacao da change.
