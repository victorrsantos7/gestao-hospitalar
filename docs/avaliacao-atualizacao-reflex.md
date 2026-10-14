# Avaliação de atualização do Reflex

## Decisão

O ambiente principal permanece em **Reflex 0.9.12**. A versão estável candidata
**0.10.0** foi avaliada em um ambiente virtual externo ao repositório e não
passou por todos os gates definidos.

## Evidências

| Gate | Resultado |
|---|---|
| Resolução de dependências | Passou após deixar o Reflex 0.10.0 resolver as versões compatíveis dos pacotes `reflex-*` |
| Suíte automatizada | Falhou: 112 testes executados, 42 erros e 1 teste de integração ignorado |
| Compilação `reflex compile --dry` | Passou |
| Smoke test HTTP | Passou com HTTP 200 em `http://localhost:3100` |

Na versão candidata, os 42 erros possuem a mesma causa: os testes atuais instanciam
`AuthState` diretamente e a versão 0.10.0 passou a esperar o atributo interno
`_was_touched` ao alterar variáveis de estado. O erro observado foi:

```text
AttributeError: 'gestao_hospitalar.auth_state.AuthState' object has no attribute '_was_touched'
```

A primeira tentativa de instalar o manifesto apenas trocando `reflex` e
`reflex-base` também foi rejeitada corretamente pelo resolvedor, porque
`reflex==0.10.0` exige `reflex-components-code>=0.10.0` e o manifesto atual fixa
`0.9.6`. O ambiente isolado foi então recriado permitindo que o Reflex
selecionasse o conjunto compatível de componentes.

## Impacto e próxima revisão

Não houve alteração em `requirements.txt` nem na `.venv` principal. Atualizar
para 0.10.0 exigiria adaptar a estratégia de instanciação de State nos testes e
regenerar de forma controlada todos os pins `reflex-*`. Isso deve ocorrer em
change própria, sem pressão da apresentação.

Como limitação separada, a suíte no working tree principal já possui 15 erros
causados por testes de edição/relatórios que não correspondem aos módulos
funcionais atualmente presentes. Essa divergência pré-existente não foi
restaurada automaticamente nesta change e precisa ser resolvida antes de o
preflight final ser aprovado.

A documentação atual também informa que `rx.Model` está depreciado desde
0.9.2 e previsto para remoção na versão 1.0. O projeto não deve introduzir novos
modelos baseados nessa API; o SQLite legado deve ser tratado conforme
[migrações locais](./migracoes-locais.md).
